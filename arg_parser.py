#! /usr/bin/python

from shapes.shape_update import ShapeUpdate
from mturk.MturkHandler import MturkHandler
import random
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from multiprocessing.pool import ThreadPool

here = os.path.dirname(os.path.abspath(__file__))+'/'


def choose_random_slides():
    # Add the range of each subject
    subjects = [range(2, 41), range(41, 131), range(131, 163)]

    slides_lst = []

    for subj in subjects:
        # k says how many slides to take from each subject
        slides_lst += random.sample(subj, k=3)

    return slides_lst

def parse_subccmd(sub_cmd, arguments):
    if sub_cmd == 'update':
        parse_update(arguments)
    elif sub_cmd == 'mturk':
        parse_mturk(arguments)
    elif sub_cmd == 'firebase':
        parse_firebase(arguments)

def parse_update(args):
    file_path = args['file_path']
    output = args['output']
    slide_nums = args['slide_num']
    shape_update = ShapeUpdate(file_path, output)
    if slide_nums:
        for number in slide_nums:
            shape_update.update_svg_by_num(number)
    else:
        shape_update.update_svg()

def parse_mturk(args):
    sub_turk_cmd = args['mturkcmd']
    prod = args['production']
    if sub_turk_cmd == 'read':
        mturk_read(production = prod)
    elif sub_turk_cmd == 'write':
        title = args['title']
        slides_lst = args['choose']
        if slides_lst is None:
            slides_lst = choose_random_slides()
        mturk_write(title, slides_lst,production = prod)
    elif sub_turk_cmd == 'create':
        title = args['title']
        svg_dir = args.get('svg_dir','public/docs/svg')
        slides_per_hit = args.get('num',20)
        limit_hits = float(args.get('count',float('inf')))
        lifetime = args.get('lifetime',600)
        mturk_create_all_hits(title=title,
                            svg_dir=svg_dir,
                            slides_per_hit=slides_per_hit,
                            limit_hits=limit_hits,
                            lifetime=lifetime,
                            production=prod)
    elif sub_turk_cmd =='delete':
        mturk_delete_all_hits()
    elif sub_turk_cmd =='review':
        mturk_review(auto=args['auto'],production=prod)

def parse_firebase(args):
    sub_cmd = args['firebasecmd']

    if sub_cmd == 'read':
        print(firebase_read(args['path']))
    
    if sub_cmd == 'read-slides':
        print(firebase_read_slides())

def mturk_read(production=False):
    mturk_handler = MturkHandler(production)
    print("hits:",mturk_handler.read_hits())
    print('account balance:',mturk_handler.get_account_balance())

def mturk_write(title, slides_lst,production=False):
    mturk_handler = MturkHandler(production)
    mturk_handler.create_hit(title, slides_lst)

def mturk_review(auto=False,bonus_amount=0.6,production=False):
    mturk = MturkHandler(production=production)
    hits = firebase_read('hits')
    if hits is None:
        print("no hits to review")
        return
    hit_ids = hits.keys()
    for hit_id in hit_ids:
        hit = mturk.get_hit(hit_id)['HIT']
        del hit['Question']
        hit['Expiration'] = hit['Expiration'].timestamp()
        hit['CreationTime'] = hit['CreationTime'].timestamp()
        firebase_write(hit['HITId'],hit,path='hits')

        if hit['HITStatus'] in ['Assignable','Unassignable']:
            continue
        assignments = mturk.get_assignments(hit_id)
        # mturk.client.update_hit_review_status(HITId=hit_id,Revert=False)
        for assignment in assignments:
            if assignment['AssignmentStatus']=='Submitted':
                if auto:
                    mturk_review_assignment(assignment,mturk,bonus_amount=bonus_amount,production=production)
                else:
                    status = assignment['AssignmentStatus']
                    data = next(iter(firebase_read(path=f"/workers/{assignment['WorkerId']}").values()),{})
                    hit = data.get('hit',{})
                    moves = [len(v.get('moves',{}))>0 for k,v in hit.items()]
                    percent_answerd = sum(moves)/len(moves)
                    assignment_id = assignment['AssignmentId']
                    worker_id = assignment['WorkerId']
                    print(f'assignment id:{assignment_id}')
                    print(f'percent answerd:{percent_answerd}')
                    print(f'status:{status}')
                    print("approve?[Y/n]")
                    res = input().lower()
                    if res =='n':
                        print("reject message:")
                        msg = input()
                        mturk.reject_assignment(assignment_id,msg)
                    else:
                        mturk.approve_assignment(assignment_id)
                        print("grant bonus?[y/N]")
                        ans = input().lower()
                        if ans=='y':
                            mturk.send_bonus(worker_id,assignment_id,bonus_amount,"You have answerd all questions, and earned a Bonus.")
        print("reviewed:",hit_id)
        firebase_delete(hit_id,'hits')
    print("all assignments reviewed")

def mturk_review_assignment(assignment,mturk=None,bonus_amount=0.6,production=False):
    if assignment['AssignmentStatus']!='Submitted':
        print('assignment alredy reviewed')
        return
    # get mturk instance
    if mturk is None:
        mturk = MturkHandler(production)

    # read assignment data from firebase
    assignment_data=next(iter(firebase_read(path=f"/workers/{assignment['WorkerId']}").values()),{})
    hit = assignment_data.get('hit',{})
    # hit = pd.DataFrame(assignment_data.get('hit',{})).T
    if len(hit)==0:
        print("hit hot found in database (probably due to validation error), rejecting assignment")
        #TODO hangle error
        mturk.reject_assignment(assignment['AssignmentId'])
        return

    # handle hit, approve or reject, send bonus if needed
    moves = [len(v.get('moves',{}))>0 for k,v in hit.items()]
    percent_answerd = sum(moves)/len(moves)

    print('reviewing',assignment['AssignmentId'])
    print(assignment['AssignmentStatus'])

    if percent_answerd>0:
        print(f"assignment {assignment['AssignmentId']} approved")
        mturk.approve_assignment(assignment['AssignmentId'])
        if percent_answerd==1:
            print(f"assignment {assignment['AssignmentId']} got a bonus")
            mturk.send_bonus(assignment['WorkerId'],assignment['AssignmentId'],bonus_amount,"You have answerd all questions, and earned a Bonus.")
    else:
        print(f"assignment {assignment['AssignmentId']} rejected")
        mturk.reject_assignment(assignment['AssignmentId'],"You havn't answerd enough questions.")

def mturk_revirew_all_assignments(production=False):
    mturk = MturkHandler(production)

    hits = firebase_read('hits')
    # hits = mturk.read_reviewable_hits()['HITs']
    while len(hits)!=0:
        print(hits)
        for hit in hits:
            assignments = mturk.get_assignments(hit['HITId'])
            mturk.client.update_hit_review_status(HITId=hit['HITId'],Revert=False)
            for assignment in assignments:
                if assignment['AssignmentStatus']=='Submitted':
                    mturk_review_assignment(assignment,mturk)

        hits = mturk.read_reviewable_hits()

def mturk_delete_all_hits(production=False):
    """
    Delete all available Hits
    """
    def del_hit(hit):
        status = hit['HITStatus']
        hit_id = hit['HITId']
        if status in ['Assignable','Unassignable']: # if hit is not expired, update experation date
            mturk.update_expiration(hit_id,datetime(2020,1,1))
            print('expiration updated:',hit_id)
        elif status in ['Reviewable','Reviewing']:
            # review all hits assignments
            assignments = mturk.get_assignments(hit_id)
            for assignment in assignments:
                if assignment['AssignmentStatus']=='Submitted':
                    mturk_review_assignment(assignment,mturk)
            # delete hit
            mturk.delete_hit(hit_id)
            print("hit",hit_id,'deleted')

    pool = ThreadPool(10)
    mturk = MturkHandler(production)
    hits = mturk.read_hits()['HITs']
    while(len(hits)!=0):
        pool.map(del_hit,hits)
        hits = mturk.read_hits()['HITs']
    
def mturk_create_all_hits(title,svg_dir='public/docs/svg',slides_per_hit=20,limit_hits=float('inf'),lifetime=600,production=False):
    ''' 
    Create all required hits
    '''
    #list all files
    file_list = sorted([file for file in os.listdir(svg_dir) if os.path.isfile(os.path.join(svg_dir,file))])
    file_groups = [[file[:-4] for file in file_list if file.startswith(f'group{group:02d}')] for group in range(1,16)]
    num_hit = max([len(i) for i in file_groups])

    #generate all hits
    hits = []
    for idx in range(int(min(num_hit,limit_hits))):
        hit=[]
        for i in range(slides_per_hit):
            if i<len(file_groups):
                lst = file_groups[i]
                if idx<len(lst):
                    hit.append(lst[idx])
                else:
                    hit.append(lst[random.randint(0,len(lst)-1)])
            else:
                lst = file_groups[random.randint(0,len(file_groups)-1)]
                rand_slide = lst[random.randint(0,len(lst)-1)]
                while(rand_slide in hit):
                    rand_slide = lst[random.randint(0,len(lst)-1)]
                hit.append(rand_slide)
        random.shuffle(hit)
        hits.append(hit)
    
    min_appruved = 1000
    min_appruved_pct = 98
    countries = ['US']
    if not production:
        min_appruved = 0
        min_appruved_pct = 0
        countries = ['US','IL']


    # create all hits
    mturk_handler = MturkHandler(production)
    pool = ThreadPool(20)
    res = pool.map(lambda hit:mturk_handler.create_hit(title, hit,lifetime=lifetime,
                                                            candidate_min_hit_approved=min_appruved,
                                                            candidate_min_hit_approved_percent=min_appruved_pct,
                                                            countries=countries),hits)
    hit_ids = [r['HIT']['HITId'] for r in res]
    for hit in res:
        del hit['HIT']['Question']
        hit['HIT']['Expiration'] = hit['HIT']['Expiration'].timestamp()
        hit['HIT']['CreationTime'] = hit['HIT']['CreationTime'].timestamp()
        firebase_write(hit['HIT']['HITId'],hit['HIT'],path='hits')
    return hit_ids

def mturk_create_colorblindness_test(production=False):
    mturk_handler = MturkHandler(production=production)

    color_qualification_test_id = mturk_handler.create_color_qualification_test()
    print(f"color qualification test created, id:{color_qualification_test_id}")

def firebase_read_slides():
    slides = firebase_read('/slides/')
    data_list=[]

    for slide_id,slide in slides.items():
        for worker_id,data in slide.items():
            for user_id,hit in data.items():
                frame = {"slide_id":slide_id,
                        "worker_id":worker_id,
                        "user_id":user_id,
                        **hit}
                data_list.append(frame)
    return data_list

def firebase_read(path='/'):
    if not firebase_admin._apps:
        # Fetch the service account key JSON file contents
        cred = credentials.Certificate('firebase-adminsdk.json')
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://goal-recognition.firebaseio.com'
        })
    ref = db.reference(path)
    return ref.get()

def firebase_write(key,data,path='/'):
    if not firebase_admin._apps:
        # Fetch the service account key JSON file contents
        cred = credentials.Certificate(here + 'firebase-adminsdk.json')
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://goal-recognition.firebaseio.com'
        })
    ref = db.reference(path)
    ref.child(key).set(data)

def firebase_delete(key,path='/'):
    if not firebase_admin._apps:
        # Fetch the service account key JSON file contents
        cred = credentials.Certificate(here + 'firebase-adminsdk.json')
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://goal-recognition.firebaseio.com'
        })
    ref = db.reference(path)
    ref.child(key).delete()
