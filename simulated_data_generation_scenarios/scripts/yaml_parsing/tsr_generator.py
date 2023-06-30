import argparse
import json
import os
import yaml
import math
import copy
import simulated_data_generation_scenarios.scripts.yaml_parsing.yaml_parsing_utils as yaml_parsing_utils


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Given path to config json, generates scene yaml with traffic signs'
    )
    parser.add_argument('config_path', type=str, help='Path to config json')
    return parser.parse_args()


def read_config(config_path):
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    return config_dict


def get_yaml_dict(template_yaml_path):
    with open(template_yaml_path, 'r') as f:
        yaml_dict = yaml.full_load(f)
    return yaml_dict


def get_ego_dict(yaml_dict):
    for agent_dict in yaml_dict['agents']:
        if agent_dict.get('ego'):
            ego_dict = agent_dict
            break
    return ego_dict


def parse_ego_dict(ego_dict):
    parsed_ego_dict = {
        'x': ego_dict['ego']['initial_position']['point']['utm']['x'],
        'y': ego_dict['ego']['initial_position']['point']['utm']['y'],
        'heading': ego_dict['ego']['initial_position']['heading']
    }
    return parsed_ego_dict


def calculate_x_y_from_ego_and_yaw(offset_list, parsed_ego_dict):
    result = list()
    prev_x = parsed_ego_dict['x']
    prev_y = parsed_ego_dict['y']
    prev_yaw = yaml_parsing_utils.wrap_angle_to_pi_range(parsed_ego_dict['heading'] + math.pi)
    for offset in offset_list:
        x_offset, y_offset = yaml_parsing_utils.transform_vector_angle_base_to_std(
                offset[:-1], yaml_parsing_utils.wrap_angle_to_pi_range(prev_yaw + math.pi)
            )
        prev_x = prev_x + x_offset  # also acts as current x, y, yaw
        prev_y = prev_y + y_offset
        prev_yaw = prev_yaw + offset[-1]
        result.append((float(prev_x), float(prev_y), prev_yaw))
    return result


def generate_sign_dicts(sign_template_dict, sign_position_and_yaw_list, base_id):
    result = list()
    for index, position_and_yaw in enumerate(sign_position_and_yaw_list, start=base_id):
        x, y, yaw = position_and_yaw  # todo change name position and yaw, maybe ad class
        next_sign = copy.deepcopy(sign_template_dict)
        next_sign['static_obstacle']['id'] = index
        next_sign['static_obstacle']['initial_state']['pose_spec']['px'] = x
        next_sign['static_obstacle']['initial_state']['pose_spec']['py'] = y
        next_sign['static_obstacle']['initial_state']['pose_spec']['rpy']['yaw'] = yaw
        result.append(next_sign)
    return result


def main(config_path):
    config_dict = read_config(config_path)
    yaml_dict = get_yaml_dict(config_dict['template_yaml_path'])
    ego_dict = get_ego_dict(yaml_dict)
    config_dict['parsed_ego_dict'] = parse_ego_dict(ego_dict)
    ready_signs = list()
    base_id = 1
    for offset_list in [config_dict['left_list'], config_dict['right_list']]:
        sign_position_and_yaw_list = calculate_x_y_from_ego_and_yaw(offset_list, config_dict['parsed_ego_dict'])
        ready_signs.extend(generate_sign_dicts(config_dict['sign_template_dict'], sign_position_and_yaw_list, base_id))
        base_id += len(ready_signs)

    destination_yaml_path = os.path.join(config_dict['destination_dir'], config_dict['destination_name'] + '.scn.yaml')
    new_agents_list = [ego_dict]
    new_agents_list.extend(ready_signs)
    yaml_dict['agents'] = new_agents_list
    with open(destination_yaml_path, 'w+') as f:
        yaml.dump(yaml_dict, f)


if __name__ == '__main__':
    args = _parse_args()
    main(args.config_path)
