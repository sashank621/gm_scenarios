import yaml
import json
import os

from typing import List, Union

from simulated_data_generation_scenarios.scripts.yaml_parsing.permutators import SignYawPerm
from simulated_data_generation_scenarios.scripts.yaml_parsing.permutators import SignTypePerm
from simulated_data_generation_scenarios.scripts.yaml_parsing.permutators import PostHeightPerm
from simulated_data_generation_scenarios.scripts.yaml_parsing import static_obstacle
from simulated_data_generation_scenarios.scripts.yaml_parsing.scenario import Scenario
import datetime
import random
import argparse
import copy

HOME = os.environ.get('HOME')
ULTRACRUISE = os.path.join(HOME, 'projects', 'uc_workspace', 'ultracruise')


class PermConfig:
    def __init__(self, perm_config_dict: dict):
        self.config_dict = copy.deepcopy(perm_config_dict)
        self.scenario_repository_path = os.path.join(ULTRACRUISE, perm_config_dict['repository'])
        self.destination_dir = os.path.join(self.scenario_repository_path, perm_config_dict['destination_dir'])
        self.destination_filename = perm_config_dict['destination_filename']
        self.parent_dir_prefix = perm_config_dict.get('parent_dir_prefix')
        self.total_num_of_scenes = perm_config_dict['total_num_of_scenes']
        self.template_scenario = self._load_template_scenario(os.path.join(self.scenario_repository_path,
                                                                           perm_config_dict['template_yaml_path']))
        self.sub_batches_dict = self.parse_batch_distribution(perm_config_dict.get('batch_distributions'))
        self.yaw_permutator = SignYawPerm(perm_config_dict.get('sign_yaw_perm'))
        self.post_height_perm_dict = perm_config_dict.get('post_height_dist')
        self.sign_type_perm_dict = perm_config_dict.get('sign_type_perm')
        self.tsr_dilution_rate = perm_config_dict.get('tsr_dilution')
        self.timestamp = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        self._set_seed()

    @staticmethod
    def _load_template_scenario(template_yaml_path):
        with open(template_yaml_path, 'r') as f:
            yaml_as_dict = yaml.full_load(f)
        return Scenario(yaml_as_dict)

    def get_marked_destination(self):
        if self.config_dict.get("timestamp_destination"):
            return os.path.join(self.destination_dir, self.timestamp)
        else:
            return self.destination_dir

    def parse_batch_distribution(self, batch_dist_dict: dict):
        sub_batches_dict = copy.deepcopy(batch_dist_dict)
        weight_sum = sum([x['weight'] for x in sub_batches_dict.values()])
        scene_per_weight_unit = self.total_num_of_scenes / weight_sum
        for sub_batch in sub_batches_dict.values():
            scene_count = sub_batch['weight'] * scene_per_weight_unit
            if not (isinstance(scene_count, int) or scene_count.is_integer()):  # not an integer
                raise ValueError('Batch distribution weights and total scene count are not possible,'
                                 ' please adjust weights')
            sub_batch['scene_count'] = int(scene_count)
        return sub_batches_dict

    def _set_seed(self):
        random_seed = self.config_dict.get('random_seed')
        if not random_seed:  # explicitly set a "random" seed and keep it for traceability
            random_seed = random.randint(0, 1000000)  # arbitrary range
            self.config_dict['random_seed'] = random_seed
        random.seed(random_seed)


def load_config_dict_from_file(perm_config_path):
    with open(perm_config_path, 'r') as f:
        perm_config_dict = json.load(f)
    return perm_config_dict


def create_dir_structure(perm_config):
    os.makedirs(perm_config.destination_dir, exist_ok=True)
    marked_destination = perm_config.get_marked_destination()
    os.makedirs(perm_config.get_marked_destination(), exist_ok=True)
    config_dir_path = os.path.join(marked_destination, 'config')
    os.mkdir(config_dir_path)
    with open(os.path.join(config_dir_path, 'config.json'), 'w+') as f:
        json.dump(perm_config.config_dict, f, indent=4)
    with open(os.path.join(config_dir_path, 'template.yaml'), 'w+') as f:
        yaml.dump(perm_config.template_scenario.scenario_dict, f)
    for sub_batch_name in perm_config.sub_batches_dict.keys():
        os.mkdir(os.path.join(marked_destination,
                              get_sub_batch_dir_name(sub_batch_name,
                                                     perm_config.parent_dir_prefix)))


def generate_yaml_full_path(perm_config: PermConfig, perm_index: int, sub_batch_name: str):
    filename = f'{perm_config.destination_filename}_{str(perm_index)}_{get_sub_batch_dir_name(sub_batch_name)}.scn.yaml'
    return os.path.join(perm_config.get_marked_destination(),
                        get_sub_batch_dir_name(sub_batch_name, perm_config.parent_dir_prefix),
                        filename)


def create_yaml_permutation(permutated_scenario: Scenario, yaml_full_path):
    with open(yaml_full_path, 'w+') as file:
        yaml.dump(permutated_scenario.scenario_dict, file)


def permutate_tsr(traffic_sign: static_obstacle.TrafficSign, sign_description):
    traffic_sign.set_sign_type(sign_description)


def get_sub_batch_dir_name(sub_batch_name_in_config, dir_prefix=None):
    sub_batch_name = sub_batch_name_in_config.lower().replace(':', '_')
    return '_'.join([x for x in [dir_prefix, sub_batch_name] if x])


def adjust_to_sub_batch(template_scenario: Scenario, sub_batch_description: dict):
    sub_batch_type = sub_batch_description['type']
    sub_batch_value = sub_batch_description['value']
    if sub_batch_type == 'sign wear':
        for obstacle in template_scenario.obstacle_list:
            if isinstance(obstacle, static_obstacle.TrafficSign):
                obstacle.set_wear(sub_batch_value)
    elif sub_batch_type == 'weather':
        template_scenario.set_weather_from_preset(sub_batch_value)
    else:
        raise ValueError('Only supports sign wear and weather sub batch type!!!')


def get_tsr_diluted_scenes(full_scene_template: Scenario, scene_count: int, tsr_dilution_rate: Union[float, None]) -> List[Scenario]:
    diluted_scenes = list()
    for i in range(scene_count):
        next_scene = full_scene_template.get_copy()
        if tsr_dilution_rate:
            next_scene.dilute_traffic_signs(tsr_dilution_rate)
        diluted_scenes.append(next_scene)

    return diluted_scenes


def generate_permutations(perm_config: PermConfig):
    for sub_batch_name, sub_batch_data in perm_config.sub_batches_dict.items():
        print(f'Generating {sub_batch_data["scene_count"]} YAMLs for sub batch "{sub_batch_name}"')
        sub_batch_templates = get_tsr_diluted_scenes(perm_config.template_scenario.get_copy(),
                                                     sub_batch_data['scene_count'],
                                                     perm_config.tsr_dilution_rate)
        total_batch_tsr_count = sum([scene.tsr_amount for scene in sub_batch_templates])
        sign_type_permutator = SignTypePerm(perm_config.sign_type_perm_dict,
                                            total_batch_tsr_count)
        post_height_permutator = PostHeightPerm(perm_config.post_height_perm_dict,
                                                total_batch_tsr_count)
        for i, scenario in enumerate(sub_batch_templates):
            adjust_to_sub_batch(scenario, sub_batch_data)
            sign_type_permutator.apply_permutation(scenario)
            post_height_permutator.apply_permutation(scenario)
            perm_config.yaw_permutator.apply_permutation(scenario)
            yaml_full_path = generate_yaml_full_path(perm_config, i, sub_batch_name)
            scenario.update_scene_name(os.path.basename(yaml_full_path))
            create_yaml_permutation(scenario, yaml_full_path)


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Generate permutated YAML files for a template scenario, according to a config json'
    )
    parser.add_argument('config_path', type=str, help='Path to permutation config json')
    return parser.parse_args()


def main(perm_config_dict):
    perm_config = PermConfig(perm_config_dict)
    create_dir_structure(perm_config)
    generate_permutations(perm_config)
    print(f'Done\nPermutations can be found in destination path {perm_config.get_marked_destination()}')


if __name__ == '__main__':
    args = _parse_args()
    main(load_config_dict_from_file(args.config_path))
