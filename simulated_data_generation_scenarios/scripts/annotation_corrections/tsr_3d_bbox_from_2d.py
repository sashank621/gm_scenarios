import argparse
import json
import os

def generate_3d_bbox_corrected_annotations_json(annotations):
    for field in annotations['annotations']:
        frame_count = 0
        for frame in annotations['annotations'][field]:
            # create 3d_bbox only if currently null
            if (frame['bbox3']['corners_3d_on_image'] == None):
                x0 = frame['bbox'][0]
                y0 = frame['bbox'][1]
                x1 = frame['bbox'][2]
                y1 = frame['bbox'][3]
                # make sure x0,y0 is bottom left and x1,y1 is top right
                if (x1 < x0): x0, x1 = x1, x0
                if (y1 < y0): y0, y1 = y1, y0
                # Create 4 front points = 4 back points such that:
                #   8 corner projection of the cuboid onto the image. The points order
                #   Show be according to the following figure, where x marks the front of the car:
                #       1-------0
                #      /       /|
                #     /       / |
                #   2--------3  |
                #   | \    / |  |
                #   |  \ /   |  4
                #   | / \    | /
                #   | /   \  |/
                #   6-------7
                # points 2,3,6,7 are equal to points 1,0,5,4 respectively
                points_3d_x = [x1,x0,x0,x1,x1,x0,x0,x1]
                points_3d_y = [y0,y0,y0,y0,y1,y1,y1,y1] #this is the correct ordering, checked manually
                frame['bbox3']['corners_3d_on_image'] = [points_3d_x,points_3d_y]
                annotations['annotations'][field][frame_count] = frame
            frame_count += 1
    return annotations

def run():
    parser = argparse.ArgumentParser(
        description='Create 3d bbox for TSR only from 2d bbox in the given annotations json')
    parser.add_argument('annotation_json_path', type=str)
    args = parser.parse_args()
    with open(args.annotation_json_path, 'r') as fileread:
        annotations = json.load(fileread)
    annotations_corrected = generate_3d_bbox_corrected_annotations_json(annotations)
    #remove annotations json and rewrite
    os.remove(args.annotation_json_path)
    with open(args.annotation_json_path, 'x') as filewrite:
        json.dump(annotations, filewrite)

if __name__ == "__main__":
    run()

