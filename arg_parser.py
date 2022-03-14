from shapes.shape_update import ShapeUpdate
from mturk.MturkHandler import MturkHandler
import random
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd


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

    if sub_turk_cmd == 'read':
        mturk_read()
    elif sub_turk_cmd == 'write':
        title = args['title']
        slides_lst = args['choose']

        if slides_lst is None:
            slides_lst = choose_random_slides()

        mturk_write(title, slides_lst)

    elif sub_turk_cmd == 'create':
        title = args['title']
        svg_dir = args.get('svg_dir','docs/svg')
        slides_per_hit = args.get('slides_per_hit',20)
        limit_hits = args.get('limit_hits',float('inf'))
        lifetime = args.get('lifetime',600)
        
        mturk_create_all_hits(title=title,
                            svg_dir=svg_dir,
                            slides_per_hit=slides_per_hit,
                            limit_hits=limit_hits,
                            lifetime=lifetime)
    elif sub_turk_cmd =='delete':
        mturk_delete_all_hits()
    elif sub_turk_cmd =='review':
        mturk_revirew_all_assignments()

def mturk_read():
    mturk_handler = MturkHandler()
    print(mturk_handler.read_hits())

def mturk_write(title, slides_lst):
    mturk_handler = MturkHandler()
    mturk_handler.create_hit(title, slides_lst)

def mturk_review_assignment(assignment,mturk=None):
    if assignment['AssignmentStatus']!='Submitted':
        print('assignment alredy reviewed')
        return
    # get mturk instance
    if mturk is None:
        mturk = MturkHandler()

    # read assignment data from firebase
    assignment_data=next(iter(firebase_read(path=f"/workers/{assignment['WorkerId']}").values()),{})
    hit = pd.DataFrame(assignment_data.get('hit',{})).T
    if len(hit)==0:
        print("ERROR: hit hot found!!")
        #TODO hangle error
        return

    # handle hit, approve or reject, send bonus if needed
    percent_answerd =1-(hit.moves.isna().sum()/len(hit.moves))
    print('reviewing',assignment['AssignmentId'])
    print(assignment['AssignmentStatus'])

    if percent_answerd>0.8:
        print(f"assignment {assignment['AssignmentId']} approved")
        mturk.approve_assignment(assignment['AssignmentId'])
        if percent_answerd==1:
            print(f"assignment {assignment['AssignmentId']} got a bonus")
            mturk.send_bonus(assignment['WorkerId'],assignment['AssignmentId'],0.1,"You have answerd all questions, and earned a Bonus.")
    else:
        print(f"assignment {assignment['AssignmentId']} rejected")
        mturk.reject_assignment(assignment['AssignmentId'],"You havn't answerd enough questions.")

def mturk_revirew_all_assignments():
    mturk = MturkHandler()
    hits = mturk.read_reviewable_hits()['HITs']
    while len(hits)!=0:
        print(hits)
        for hit in hits:
            assignments = mturk.get_assignments(hit['HITId'])
            mturk.client.update_hit_review_status(HITId=hit['HITId'],Revert=False)
            for assignment in assignments:
                if assignment['AssignmentStatus']=='Submitted':
                    mturk_review_assignment(assignment,mturk)

        hits = mturk.read_reviewable_hits()

def mturk_delete_all_hits():
    """
    Delete all available Hits
    """
    mturk = MturkHandler()
    hits = mturk.read_hits()['HITs']
    while(len(hits)!=0):
        for hit in hits:
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
        hits = mturk.read_hits()['HITs']
    
def mturk_create_all_hits(title,svg_dir='docs/svg',slides_per_hit=20,limit_hits=float('inf'),lifetime=600):
    ''' 
    Create all required hits
    '''
    #list all files
    file_list = sorted([file for file in os.listdir(svg_dir) if os.path.isfile(os.path.join(svg_dir,file))])
    file_groups = [[file[:-4] for file in file_list if file.startswith(f'group{group:02d}')] for group in range(1,16)]
    num_hit = max([len(i) for i in file_groups])
    mturk_handler = MturkHandler()

    for idx in range(min(num_hit,limit_hits)):
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
        mturk_handler.create_hit(title, hit,lifetime=lifetime)

def firebase_read_all():
    slides = firebase_read('/slides/')
    data_list=[]

    for slide_id,slide in slides.items():
        for worker_id,data in slide.items():
            for assignment_id,hit in data.items():
                frame = {"slide_id":slide_id,
                        "worker_id":worker_id,
                        "assignment_id":assignment_id,
                        **hit}
                data_list.append(frame)
    return pd.DataFrame(data_list)

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

