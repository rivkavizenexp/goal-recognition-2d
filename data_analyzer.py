from firebase_utils import firebase_handler
import pandas as pd
import math
from bs4 import BeautifulSoup
import argparse
import os
import json
import numpy as np
from tqdm import tqdm

def get_report(anchors):

    print('Reading data from firebase...')
    firebase = firebase_handler()
    slides = firebase.read('slides')
    assignments = []
    for slide,data in slides.items():
        for worker,assignment in data.items():
            assignments.append({'slide':slide,'worker':worker,**next(iter(assignment.values()))})
    slides_df = pd.DataFrame(assignments)
    workers = firebase.read('workers')
    workers_df = pd.DataFrame({k:next(iter(v.values())) for k,v in workers.items()}).T
    print('Number of workers:',len(workers_df),'Number of assignments:',len(slides_df))

    # get the final location of the dynamic object
    slides_df['final_location'] = slides_df['final_locations'].apply(lambda x:[(i['x'],i['y']) for i in x if i['src'] == 'dynamic'][0])
    
    # get final location quarter:
    # ________
    # | 1 | 2 |
    # |___|___|
    # | 3 | 4 |
    # |___|___|
    slides_df['quarter'] = slides_df['final_location'].apply(lambda cord:(1 if cord[0] < 640 else 0)+(2 if cord[1]< 360 else 0) )
    
    # get distance from anchor:

    def get_distance_from_anchor(row):
        if row['slide'] not in anchors:
            return np.nan
        anchor = anchors[row['slide']]
        final_location = row['final_location']
        return math.sqrt((final_location[0]-anchor[0])**2+(final_location[1]-anchor[1])**2)
    slides_df['distance_from_anchor'] = slides_df[['final_location','slide']].apply(get_distance_from_anchor,axis=1)
    def is_inside_anchor(row):
        return np.nan if row['slide'] not in anchors else row['distance_from_anchor'] < anchors[row['slide']][2]
    slides_df['is_insde_anchor'] = slides_df[['distance_from_anchor','slide']].apply(is_inside_anchor,axis=1)

    return slides_df.join(workers_df.drop('AssignmentId',axis=1),on='worker').drop('hit',axis=1)


def create_tag(relative_moves):
    if isinstance(relative_moves,float) :
        return ''
    path = "M 0.0 0.0 " + ' '.join([f"L {m['x']} {m['y']}" for m in relative_moves])
    tag = f'<animateMotion dur="2s" fill="freeze" id="entrance_motion" begin="5s;" path="{path}"/>'
    return tag

def create_preview(slide,relative_moves,worker,anchors):
    slide_name = slide.split('-')[1]


    # if svg exist on the svg folder, use it, otherwise use the svg_old folder
    # TODO absolute path
    path = f"public/docs/svg/{slide_name}.svg" if os.path.exists(f"public/docs/svg/{slide_name}.svg") else f"public/docs/svg_old/{slide_name}.svg"
    with open(path) as file:
        text=file.read()
        soup = BeautifulSoup(text, 'xml')
        object_tag = soup.find("svg", { "id" : "dynamic" }).find('path')
        anim = object_tag.find('animateMotion')
        x,y = 0,0
        if anim:
            x,y = object_tag.find('animateMotion').get('path').split(' ')[-2:]
            x,y = float(x),float(y)
        path = f"M {x} {y} "
        if not isinstance(relative_moves,float):
            if isinstance(relative_moves,str):
                relative_moves = json.loads(relative_moves.replace("'",'"'))
            path += ' '.join([f"L {x+m['x']} {y+m['y']}" for m in relative_moves])

        new_tag = soup.new_tag("animateMotion", dur="2s",fill="freeze", begin="5s;", path=path)

        object_tag.insert(3,new_tag)

        # add anchor to the svg
        x,y,r = anchors.get(slide,(None,None,None))
        if x and y and r:
            anchor_circle = soup.new_tag("circle", cx=x, cy=y, r=r, fill="transparent", stroke="black", stroke_width="2")
            anchor_center = soup.new_tag("circle", cx=x, cy=y, r=5, fill="black", stroke="black", stroke_width="2")
            anchor_circle.attrs['stroke-dasharray']='5'
            anchor_tag = soup.new_tag("g", id="anchor")
            anchor_tag.insert(0,anchor_circle)
            anchor_tag.insert(1,anchor_center)
            soup.find("svg").insert(0,anchor_tag)

        # add quarters to the svg
        horizontal = soup.new_tag("line", x1=640, y1=0, x2=640, y2=720, stroke="black")
        horizontal.attrs['stroke-dasharray']='5'
        vertical = soup.new_tag("line", x1=0, y1=360, x2=1280, y2=360, stroke="black")
        vertical.attrs['stroke-dasharray']='5'
        
        text_atrrs = {'font-size':"60",'fill':"gray",'text-anchor':"middle",'alignment-baseline':"middle"}
        quarter1_text = soup.new_tag("text", x=320, y=180)
        quarter1_text.attrs.update(text_atrrs)
        quarter1_text.string = "1"
        quarter2_text = soup.new_tag("text", x=960, y=180)
        quarter2_text.attrs.update(text_atrrs)
        quarter2_text.string = "2"
        quarter3_text = soup.new_tag("text", x=320, y=540)
        quarter3_text.attrs.update(text_atrrs)
        quarter3_text.string = "3"
        quarter4_text = soup.new_tag("text", x=960, y=540)
        quarter4_text.attrs.update(text_atrrs)
        quarter4_text.string = "4"
        quarter_tag = soup.new_tag("g", id="quarters")
        quarter_tag.insert(0,horizontal)
        quarter_tag.insert(1,vertical)
        quarter_tag.insert(2,quarter1_text)
        quarter_tag.insert(3,quarter2_text)
        quarter_tag.insert(4,quarter3_text)
        quarter_tag.insert(5,quarter4_text)
        soup.find("svg").insert(0,quarter_tag)


        # save the svg
        os.makedirs("workloads",exist_ok=True)
        with open(f"workloads/{slide_name}_{worker}.svg",'w') as res:
            res.write(str(soup))

def get_anchors_normlized(anchors_file, ratioX, ratioY):
    anchors_df = pd.read_excel(anchors_file)
    anchors_df['slide'] = anchors_df.apply(lambda x:f"svg-group{int(x['Group']):02d}_slide{int(x['Slide']):02d}",axis=1)
    anchors_df.index = anchors_df['slide']

    anchors_df['x'] = anchors_df['x']*ratioX
    anchors_df['y'] = anchors_df['y']*ratioY
    anchors_df['Radius'] = anchors_df['Radius']*(ratioX + ratioY)/2
    anchors = {label:(data['x'],data['y'],data['Radius']) for label,data in anchors_df[['x','y','Radius']].T.to_dict().items()}
    return anchors

def create_parser():
    parser = argparse.ArgumentParser( description='Analyze experience data from firebase, and create a report')
    parser.add_argument('--output_path', type=str, default='report.csv', help='path to save the report')
    parser.add_argument('--anchors_file',type=str, default=None, help="path for input anchors csv file")
    parser.add_argument('--preview', action='store_true', help='create preview for each slide')
    return parser

def parse_args(args):
    anchors = {}
    if args['anchors_file']:
        anchors = get_anchors_normlized(args['anchors_file'], 1280/33, 720/18)
    report_df = get_report(anchors)
    report_df[['slide','worker','quarter','distance_from_anchor','is_insde_anchor']].to_csv(args['output_path'])
    if args['preview']:
        print("creating previews")
        for i,row in tqdm(report_df.iterrows()):
            create_preview(row['slide'],row['relative moves'],row['worker'],anchors)

if __name__ == "__main__":
    parser = create_parser()
    args = vars(parser.parse_args())
    parse_args(args)