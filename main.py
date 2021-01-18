import argparse

from bs4 import BeautifulSoup
from shapes.shape_update import ShapeUpdate
from mturk.MturkHandler import MturkHandler

def parse_arguments():
    """
    Arguemts parser.

    Returns:
        Command line arguments
    """
    ap = argparse.ArgumentParser()
    subparsers = ap.add_subparsers(dest='subcmd')

    # Update SVG options
    update_parser = subparsers.add_parser('update', help='update -h',
                                          description="Updates SVG shapes from"
                                                      " given pptx path")
    update_parser.add_argument('-f', '--file_path', type=str, required=True,
                               help="Path to new PowerPoint file containing"
                                    " test slides")
    update_parser.add_argument('-o', '--output', type=str, required=True,
                               help="Path to output directory where to store "
                                    "the new SVGs")
    update_parser.add_argument('-s', '--slide_num', type=int, nargs='+',
                               help="Update by slide numbers, "
                                    "Enter desired slide numbers. "
                                    "If not specified, all slides are updated")

    # Mturk handler option
    mturk_parser = subparsers.add_parser('mturk', help='mturk -h',
                                         description="Handles the connection "
                                                     "to MechanicalTurk")
    mturk_sub = mturk_parser.add_subparsers(title='mturk commands', dest='mturkcmd')

    read_mturk = mturk_sub.add_parser('read', help='read -h',
                                      description="Handles reading/downloading "
                                                  "data from MechanicalTurk - "
                                                  "mainly getting status "
                                                  "updates on current HITs")

    write_mturk = mturk_sub.add_parser('write', help='write -h',
                                       description="Handles writing/uploading "
                                                   "data from MechanicalTurk - "
                                                   "mainly creating HITs")
    write_mturk.add_argument('-t', '--title', type=str, required=True,
                             help="Title of the HIT")

    args = vars(ap.parse_args())
    return args


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
        mturk_write(title)


def mturk_read():
    mturk_handler = MturkHandler()
    mturk_handler.read_hits()


def mturk_write(title):
    mturk_handler = MturkHandler()
    # mturk_handler.create_hit(title)


if __name__ == '__main__':
    arguments = parse_arguments()
    print(arguments)
    sub_cmd = arguments['subcmd']
    if sub_cmd == 'update':
        parse_update(arguments)
    elif sub_cmd == 'mturk':
        parse_mturk(arguments)
