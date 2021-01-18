import argparse
from arg_parser import parse_subccmd


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
    write_mturk.add_argument('-c', '--choose', type=str, required=False,
                             help="Choose a list of slides to add to HIT")

    args = vars(ap.parse_args())
    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    sub_cmd = arguments['subcmd']
    parse_subccmd(sub_cmd, arguments)
