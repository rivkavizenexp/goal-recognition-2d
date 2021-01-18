from shapes.shape_update import ShapeUpdate
from mturk.MturkHandler import MturkHandler
import random


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


def mturk_read():
    mturk_handler = MturkHandler()
    mturk_handler.read_hits()


def mturk_write(title, slides_lst):
    mturk_handler = MturkHandler()
    mturk_handler.create_hit(title, slides_lst)
