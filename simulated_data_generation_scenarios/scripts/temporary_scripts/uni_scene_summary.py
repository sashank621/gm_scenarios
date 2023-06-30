import argparse
import json
import os


_ANNOTATION_TYPE_TSR = '6'

TOTALLY_VISIBLE_VALUE = 0
SLIGHTLY_OCCLUDED_VALUE = 1
PARTLY_OCCLUDED_VALUE = 2
MOSTLY_OCCLUDED_VALUE = 3
TOTALLY_OCCLUDED_VALUE = 5


def tsr_occlusion_rate(all_tsrs, num_of_frames):
    tsr_annotation_counter = 0
    fully_visible = '0% Occluded (Fully Visible)'
    slightly_occluded = '1-40% Occluded'
    partly_occluded = '41-75% Occluded'
    mostly_occluded = '76-99% Occluded (Nearly Covered)'
    totally_occluded = '100% Occluded (Fully Covered)'
    occlusion_counter = {
        fully_visible: 0,
        slightly_occluded: 0,
        partly_occluded: 0,
        mostly_occluded: 0,
        totally_occluded: 0,
    }
    for annotation_instance in all_tsrs:
        tsr_annotation_counter += 1
        occlusion_value = annotation_instance['occlusion']
        occlusion_counter[occlusion_value] += 1
    if tsr_annotation_counter:
        for key, value in occlusion_counter.items():
            print(f'{key}: ratio: {value / len(all_tsrs) * 100: .2f}%, count: {value}')
        print(f'tsr_annotation_counter: {len(all_tsrs)}')
        print(f'AVG TSR per frame count: {len(all_tsrs) / num_of_frames}')


def empty_frames(full_annotation_dict):
    empty_frames_counter = 0
    for timestamp in full_annotation_dict:
        for frame in timestamp['frames']:
            if not any([v for v in frame.values() if isinstance(v, list)]):
                empty_frames_counter += 1
    print(f'Empty frames counter: {empty_frames_counter}')


def get_annotations_for_type(full_annotation_dict, annotation_type_key):
    annotation_instances = []
    for timestamp in full_annotation_dict:
        for frame in timestamp['frames']:
            annotation_instances.extend(frame[annotation_type_key])
    return annotation_instances


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Provide summary of annotation contents of tsr scene, according to a config json'
    )
    parser.add_argument('config_path', type=str, help='Path to config json')
    return parser.parse_args()


def _parse_annot_json(config_path):
    with open(config_path, 'r') as f:
        data = json.load(f)
    dicts = list()
    for name in data['scene_name']:
        annot_path = os.path.join(data['processing_dir'], name, 'postprocessed_annotations', 'unified_annotations.json')  # todo revert to annotations.json
        with open(annot_path, 'r') as f:
            annot_dict = json.load(f)
        dicts.append((name, annot_dict))
    return dicts


def main(full_annotation_dict):
    all_tsrs = get_annotations_for_type(full_annotation_dict, 'traffic_signs')
    all_ignore = get_annotations_for_type(full_annotation_dict, 'ignore')
    tsr_occlusion_rate(all_tsrs, len(full_annotation_dict))
    empty_frames(full_annotation_dict)
    print(f'total tsr + ignore annotations: {len(all_tsrs) + len(all_ignore)}\n')


if __name__ == "__main__":
    args = _parse_args()
    for name, annot_dict in _parse_annot_json(args.config_path):
        print(name)
        main(annot_dict)

