from shapes.pptx2geo import *


class ShapeUpdate:

    def __init__(self, pptx_path, svg_dir):
        self._pptx_path = pptx_path
        self._svg_dir = svg_dir
        self._svg_extract = SvgExtract(self._pptx_path, self._svg_dir)
        # latest_file_name = "Experiment_Feb_2020_last_version.pptx"
        # svg_dir = "./docs/svg"

    def update_svg(self):
        self._svg_extract.slides_to_svg()

    def update_svg_by_num(self, slide_num):
        self._svg_extract.slide_to_svg(slide_number=slide_num)

    def update_svg_dir(self, new_svg_dir):
        self._svg_dir = new_svg_dir

    def update_pptx_path(self, new_path):
        self._pptx_path = new_path


def slides_to_svgs(files,output_dir):
    for file in files:
        svg_extract = SvgExtract(file,output_dir)
        svg_extract.slides_to_svg()

def all_slides_to_svg(input_dir,output_dir):
    files_list = sorted([os.path.join(input_dir,file) for file in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir,file)) and file.endswith('.pptx')])
    slides_to_svgs(files_list,output_dir)