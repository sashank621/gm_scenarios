import argparse
import json
import os


_ANNOTATION_TYPE_TSR = '6'

TOTALLY_VISIBLE_VALUE = 0
SLIGHTLY_OCCLUDED_VALUE = 1
PARTLY_OCCLUDED_VALUE = 2
MOSTLY_OCCLUDED_VALUE = 3
TOTALLY_OCCLUDED_VALUE = 5


def tsr_occlusion_rate(annotations_dict):
    tsr_annotation_counter = 0
    fully_visible_tsr_counter = 0
    slightly_occluded_tsr_counter = 0
    partly_occluded_tsr_counter = 0
    mostly_occluded_tsr_counter = 0
    totally_occluded_tsr_counter = 0
    for annotation_type_id, annotation_type_data in annotations_dict['annotations'].items():
        if annotation_type_id != _ANNOTATION_TYPE_TSR:
            continue
        for annotation_instance in annotation_type_data:
            tsr_annotation_counter += 1
            occlusion_value = annotation_instance['occlusion']
            if occlusion_value == 0:
                fully_visible_tsr_counter += 1
            elif occlusion_value == 1:
                slightly_occluded_tsr_counter += 1
            elif occlusion_value == 2:
                partly_occluded_tsr_counter += 1
            elif occlusion_value == 3:
                mostly_occluded_tsr_counter += 1
            elif occlusion_value == 5:
                totally_occluded_tsr_counter += 1
    if tsr_annotation_counter:
        print(f'Fully visible: ratio: {fully_visible_tsr_counter / tsr_annotation_counter * 100: .2f}%, count: {fully_visible_tsr_counter}')
        print(f'Slightly occluded: ratio: {slightly_occluded_tsr_counter / tsr_annotation_counter * 100: .2f}%, count: {slightly_occluded_tsr_counter}')
        print(f'Partly occluded: ratio: {partly_occluded_tsr_counter / tsr_annotation_counter * 100: .2f}%, count: {partly_occluded_tsr_counter}')
        print(f'Mostly occluded: ratio: {mostly_occluded_tsr_counter / tsr_annotation_counter * 100: .2f}%, count: {mostly_occluded_tsr_counter}')
        print(f'Fully occluded: ratio: {totally_occluded_tsr_counter / tsr_annotation_counter * 100: .2f}%, count: {totally_occluded_tsr_counter}')
        print(f'tsr_annotation_counter: {tsr_annotation_counter}')
        print(f'AVG TSR per frame count: {tsr_annotation_counter / len(annotations_dict["images"])}')


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Provide summary of annotation contents of tsr scene, according to a config json'
    )
    parser.add_argument('config_path', type=str, help='Path to config json')
    return parser.parse_args()


def _parse_annot_json(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    annot_path = os.path.join(data['processing_dir'], data['scene_name'], 'postprocessed_annotations', 'annotations.json')
    with open(annot_path, 'r') as f:
        annot_dict = json.load(f)
    return annot_dict


def main(full_annotation_dict):
    annotation_dict = full_annotation_dict['annotations']
    print(f'total tsr + ignore annotations: {len(annotation_dict["6"]) + len(annotation_dict["4"])}\n')
    tsr_occlusion_rate(full_annotation_dict)


if __name__ == "__main__":
    args = _parse_args()
    main(_parse_annot_json(args.config_path))

