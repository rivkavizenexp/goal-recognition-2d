#! /usr/bin/python
import argparse
from arg_parser import parse_subccmd,mturk_create_colorblindness_test


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
    

    input_group = update_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', type=str, nargs='+',
                               help="Path to new PowerPoint file containing"
                                    " test slides")
    input_group.add_argument('-i', '--input_dir', type=str,
                            help="Path to input directory containing slides")

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
    mturk_parser.add_argument('-p', '--production', action='store_true', help='production flag')
                        
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
        
    write_mturk.add_argument('-c', '--choose', type=str, required=False,
                             help="Choose a list of slides to add to HIT")

    create_mturk = mturk_sub.add_parser('create', help='create -h',
                                       description="Creates all hits "
                                                   "and uploads them to MechanicalTurk")
    create_mturk.add_argument('-t', '--title', type=str, required=True,
                             help="Title of the HIT")
    create_mturk.add_argument('-d', '--svg_dir', type=str, default='public/docs/svg', required=False,
                             help="SVGs directory")
    create_mturk.add_argument('-n', '--num', type=int, default=20, required=False,
                             help="number of slides per HIT")
    create_mturk.add_argument('-l', '--lifetime', type=int, default=60*60*24*30, required=False,
                             help="lifetime for the HIT in seconds")

    create_mturk.add_argument('-c','--count', required=False,
                            help="Maximum number of HITs to create")

    delete_mturk = mturk_sub.add_parser('delete', help='delete -h',
                                      description="Deletes all available Hits from MechanicalTurk")

    firebase_parser = subparsers.add_parser('firebase', help='firebase -h', description="Handle firebase database")
    firebase_sub = firebase_parser.add_subparsers(title='firebase commands', dest='firebasecmd')

    read_firebase = firebase_sub.add_parser('read', help='read -h',
                                        description="Handles reading/downloading data from firebase")
    read_firebase.add_argument('-p', '--path', type=str, default='/', required=False)
    
    read_slides_firebase = firebase_sub.add_parser('read-slides', help='read -h',
                                        description="read slides data from firebase")

    read_slides_firebase.add_argument('-o', '--out', type=str, default=None, required=False, help='Output file path')

    review_mturk = mturk_sub.add_parser('review', help='review -h',
                                      description="review all available Assignments on MechanicalTurk")
    
    review_mturk.add_argument('-a', '--auto', action='store_true', help='automatic review flag')

    test_mturk = mturk_sub.add_parser('make_test', help='make_test -h',
                                      description="creates color blindness test")

    report_parser = subparsers.add_parser('report', help='report -h',
                                          description="Generates a report "
                                                      "from the given data")
    report_parser.add_argument('--output_path', type=str, default='report.csv', help='Analyze experience data from firebase, and create a report')
    report_parser.add_argument('--anchors_file',type=str, default=None, help="path for input anchors csv file")
    report_parser.add_argument('--preview', action='store_true', help='create preview for each slide')

    args = vars(ap.parse_args())
    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    sub_cmd = arguments['subcmd']
    parse_subccmd(sub_cmd, arguments)
