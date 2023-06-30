import json
import os
import glob


def is_inside_frame(bbox, coord_system):
    if coord_system == 79:
        res_x = 3946
        res_y = 1412
    elif coord_system == 78:
        res_x = 3900
        res_y = 1924
    else:
        raise ValueError(f'Impossible coord system {coord_system}')
    x1, y1, x2, y2 = bbox
    return (0 < x1 < res_x) and (0 < x2 < res_x) and (0 < y1 < res_y) and (0 < y2 < res_y)


def main():
    # base_path = '/data/transfer/simulations/tsr_workshop_deliveries/batch_02/replacement_scenes_truncation'
    # annotation_paths = glob.glob(os.path.join(base_path, '*', '*', '*', '*', '*', 'annotations.json'))
    # base_path = '/data/transfer/simulations/data_generation_processing/golden_diversity_urban_right_1673359821/postprocessed_annotations'
    base_path = '/data/transfer/simulations/output_daniel/data_generation/diversity_golden_scenes/dataops_generated_recordings/2023_01_11/VIN_Simulation_En7/golden_diversity_urban_center_1673430468'
    annotation_paths = glob.glob(os.path.join(base_path, 'annotations.json'))
    for path in annotation_paths:
        with open(path, 'r') as f:
            data = json.load(f)
        for tsr_dict in data['annotations']['6']:
            if not is_inside_frame(tsr_dict['bbox'], tsr_dict['coordinate_system']):
                print(f'\nBad annotation!!\n truncation == {tsr_dict["truncation"]}\nid == {tsr_dict["id"]}\n{tsr_dict["bbox"]}\n')
            # print(tsr_dict['truncation'])
            # if tsr_dict['truncation']:
                # print(f'\nTruncated annotation!!\n id == {tsr_dict["id"]}\n{tsr_dict["bbox"]}\n')


if __name__ == '__main__':
    main()
