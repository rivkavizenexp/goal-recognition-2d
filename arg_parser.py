from shapes.shape_update import ShapeUpdate
from mturk.MturkHandler import MturkHandler
import random
import os

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
        create_all_hits(title)
    elif sub_turk_cmd =='delete':
        mturk_delete_all()

def mturk_read():
    mturk_handler = MturkHandler()
    mturk_handler.read_hits()


def mturk_write(title, slides_lst):
    mturk_handler = MturkHandler()
    mturk_handler.create_hit(title, slides_lst)

def mturk_delete_all():
    mturk_handler = MturkHandler()
    mturk_handler.delete_hits()


def create_all_hits(title):
    ''' 
    Create all required hits
    '''


    svg_dir = 'docs/svg'
    slides_per_hit=20

    #list all files
    file_list = sorted([file for file in os.listdir(svg_dir) if os.path.isfile(os.path.join(svg_dir,file))])
    file_groups = [[file[:-4] for file in file_list if file.startswith(f'group{group:02d}')] for group in range(1,16)]
    num_hit = max([len(i) for i in file_groups])

    for idx in range(num_hit):
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
                randSlide = lst[random.randint(0,len(lst)-1)]
                while(randSlide in hit):
                    randSlide = lst[random.randint(0,len(lst)-1)]
                hit.append(randSlide)
        mturk_write(title,hit)

