import os
from simulated_data_generation_scenarios.scripts.yaml_parsing import generate_yaml_permutations
from simulated_data_generation_scenarios.scripts.yaml_parsing import scenario
from simulated_data_generation_scenarios.scripts.yaml_parsing import static_obstacle
import glob
import shutil
import json
import yaml
import time
import pytest

HOME = os.environ.get('HOME')
ULTRACRUISE = os.path.join(HOME, 'projects/uc_workspace/ultracruise')
SIMULATED_DATA_GENERATION_SCENARIOS = os.path.join(ULTRACRUISE, 'simulated_data_generation_scenarios')

TIMESTAMP = str(time.time())
TEST_DIR = os.path.join(SIMULATED_DATA_GENERATION_SCENARIOS, 'test')
TEMPLATES_DIR = os.path.join(TEST_DIR, 'resources', 'unit_tests', 'yaml_parsing', 'templates')
CONFIG_JSON1_PATH = os.path.join(TEMPLATES_DIR, 'perm_generator_test_config_template1.json')
CONFIG_JSON2_PATH = os.path.join(TEMPLATES_DIR, 'perm_generator_test_config_template2.json')
CONFIG_JSON3_PATH = os.path.join(TEMPLATES_DIR, 'perm_generator_test_config_template3.json')
CONFIG_JSON4_PATH = os.path.join(TEMPLATES_DIR, 'perm_generator_test_config_template4.json')

EPSILON = 0.10
MAX_LEGAL_DISTANCE_TSRS = scenario.GUARANTEED_VIEWING_RANGE + 25


@pytest.fixture(scope='module', params=(CONFIG_JSON1_PATH, CONFIG_JSON2_PATH, CONFIG_JSON3_PATH, CONFIG_JSON4_PATH))
def scene_config(request):
    with open(request.param, 'r') as f:
        config_dict = json.load(f)
    config_dict['destination_dir'] = os.path.join(config_dict['destination_dir'], TIMESTAMP)
    generate_yaml_permutations.main(config_dict)
    config_dict['full_destination_path'] = os.path.join(ULTRACRUISE,
                                                        config_dict['repository'],
                                                        config_dict['destination_dir'])
    yield config_dict
    shutil.rmtree(config_dict['full_destination_path'])


@pytest.fixture(scope='module')
def metrics_dict(scene_config):
    data_dict = dict()
    data_dict['destination_file_paths'] = _get_destination_file_paths(scene_config)
    data_dict['template_yaml_dict'] = _get_template_yaml_dict(scene_config)
    data_dict['agents_by_id'] = _get_agents_by_id(data_dict['template_yaml_dict'])
    data_dict['permutated_yaml_dicts'] = _get_permutated_yaml_dicts(data_dict['destination_file_paths'])
    data_dict['instance_counters'] = _get_instance_counters(data_dict['permutated_yaml_dicts'])
    yield data_dict


def _get_destination_file_paths(config_dict):
    file_paths_dict = dict()
    destination_dir = os.path.join(ULTRACRUISE,
                                   config_dict['repository'],
                                   config_dict['destination_dir'])
    for subdir in glob.glob(os.path.join(destination_dir, '*')):
        file_paths_dict[os.path.basename(subdir)] = glob.glob(os.path.join(subdir, '*'))
    return file_paths_dict


def _get_template_yaml_dict(config_dict):
    template_yaml_path = os.path.join(ULTRACRUISE,
                                      config_dict['repository'],
                                      config_dict['destination_dir'],
                                      'config/template.yaml'
                                      )
    with open(template_yaml_path, 'r') as f:
        yaml_dict = yaml.full_load(f)
    return yaml_dict


def _get_agents_by_id(template_yaml_dict):
    agents_by_ids = dict()
    for agent in template_yaml_dict['agents']:
        static_obstacle_data = agent.get('static_obstacle')
        if static_obstacle_data:
            agents_by_ids[static_obstacle_data['id']] = agent
    return agents_by_ids


def _get_permutated_yaml_dicts(destination_file_paths):
    permutated_yaml_dicts = dict()
    for name in destination_file_paths.keys():
        permutated_yaml_dicts[name] = list()
    for name, contents in destination_file_paths.items():
        for path in contents:
            with open(path, 'r') as f:
                data = yaml.full_load(f)
            permutated_yaml_dicts[name].append(data)
    return permutated_yaml_dicts


def _get_instance_counters(permutated_yaml_dicts):
    instance_counters_dict = {
        'sign_types': dict(),
        'post_heights': dict(),
        'total_tsr_count': 0
    }
    for key, yaml_dict_list in permutated_yaml_dicts.items():
        if key == 'config':
            continue
        for scene_dict in yaml_dict_list:
            for agent_dict in scene_dict['agents']:
                if not _is_agent_tsr(agent_dict):
                    continue
                sign_config = agent_dict['static_obstacle']['custom_model_description']['sign_configuration']
                sign_type = _get_sign_type_name(sign_config)
                if sign_type in instance_counters_dict['sign_types']:
                    instance_counters_dict['sign_types'][sign_type] += 1
                else:
                    instance_counters_dict['sign_types'][sign_type] = 1
                post_height = sign_config['post']
                if post_height in instance_counters_dict['post_heights']:
                    instance_counters_dict['post_heights'][post_height] += 1
                else:
                    instance_counters_dict['post_heights'][post_height] = 1
                instance_counters_dict['total_tsr_count'] += 1
    return instance_counters_dict


def _is_agent_tsr(agent_dict):
    static_obstacle_dict = agent_dict.get('static_obstacle')
    if not static_obstacle_dict:
        return False
    return static_obstacle_dict.get('spectral_static_model') == 'CUSTOM_SIGN'


def _get_sign_type_name(spectral_static_model):
    preset = spectral_static_model['preset']
    if preset in static_obstacle.FALSE_ALARM_SIGNS:
        return preset
    max_speed = spectral_static_model.get('maximum_speed')
    if max_speed:
        return ':'.join([preset, str(max_speed)])
    else:
        return preset


def _check_sign_wear_sub_batch(scene_dict_list, value):
    for scene_dict in scene_dict_list:
        for agent_dict in scene_dict['agents']:
            if not _is_agent_tsr(agent_dict):
                continue
            material_dict = agent_dict['static_obstacle']['custom_model_description']['sign_configuration'].get(
                'material')
            if not material_dict:
                return False
            for key, curr_value in material_dict.items():
                if 'amount' in key and curr_value != value:
                    return False
    return True


def _check_weather_sub_batch(scene_dict_list, value):
    for scene_dict in scene_dict_list:
        if scene_dict['spectral']['environment'] != scenario.SUPPORTED_WEATHER_PRESETS[value]:
            return False
    return True


def _check_distribution(expected_distribution_dict, instance_counter_dict, total_tsr_count):
    sum_weights = sum(expected_distribution_dict.values())
    for instance_name, distribution in expected_distribution_dict.items():
        instance_count = instance_counter_dict[instance_name]
        expected_amount = total_tsr_count * distribution / sum_weights
        if not abs(expected_amount - instance_count) < expected_amount * EPSILON:
            return False
    return True


def test_total_scene_count(scene_config, metrics_dict):
    scene_count = 0
    for name, contents in metrics_dict['destination_file_paths'].items():
        if name == 'config':
            continue
        scene_count += len(contents)
    assert scene_count == scene_config['total_num_of_scenes']


def test_sub_batches_weights(scene_config, metrics_dict):
    sum_weights = sum([description['weight'] for description in scene_config['batch_distributions'].values()])
    for name, description in scene_config['batch_distributions'].items():
        expected_num_of_scenes = description['weight'] / sum_weights * scene_config['total_num_of_scenes']
        actual_num_of_scenes = len(metrics_dict['destination_file_paths'][name])
        assert expected_num_of_scenes == actual_num_of_scenes


def test_sub_batches_parameters(scene_config, metrics_dict):  # add additional types when supported
    for name, description in scene_config['batch_distributions'].items():
        if description['type'] == 'sign wear':
            assert _check_sign_wear_sub_batch(metrics_dict['permutated_yaml_dicts'][name], description['value'])
        if description['type'] == 'weather':
            assert _check_weather_sub_batch(metrics_dict['permutated_yaml_dicts'][name], description['value'])


def test_yaw_max_change(scene_config, metrics_dict):
    if not scene_config.get('sign_yaw_perm'):  # does not permutate yaw
        return
    # this function assumes the order of the agents stays the same in the template yaml dict and all permutated ones
    template_yaml_dict = metrics_dict['template_yaml_dict']
    for key, yaml_dict_list in metrics_dict['permutated_yaml_dicts'].items():
        if key == 'config':
            continue
        for permutated_scene_dict in yaml_dict_list:
            for permutated_agent in permutated_scene_dict['agents']:
                if not _is_agent_tsr(permutated_agent):
                    continue
                template_agent = metrics_dict['agents_by_id'][permutated_agent['static_obstacle']['id']]
                base_yaw = template_agent['static_obstacle']['initial_state']['pose_spec']['rpy']['yaw']
                changed_yaw = permutated_agent['static_obstacle']['initial_state']['pose_spec']['rpy']['yaw']
                assert abs(base_yaw - changed_yaw) < scene_config['sign_yaw_perm']['yaw_change_max']


def test_sign_type_distribution(scene_config, metrics_dict):
    if 'sign_type_perm' not in scene_config:
        return
    assert _check_distribution(scene_config['sign_type_perm']['sign_type_dist'],
                               metrics_dict['instance_counters']['sign_types'],
                               metrics_dict['instance_counters']['total_tsr_count'])


def test_post_height_distribution(scene_config, metrics_dict):
    if 'post_height_dist' not in scene_config:
        return
    assert _check_distribution(scene_config['post_height_dist'],
                               metrics_dict['instance_counters']['post_heights'],
                               metrics_dict['instance_counters']['total_tsr_count'])


def test_tsr_dilution(scene_config, metrics_dict):
    if not scene_config.get('tsr_dilution'):
        return
    for k, v in metrics_dict['permutated_yaml_dicts'].items():
        if k == 'config':
            continue
        for permutated_scene_dict in v:
            scenario_obj = scenario.Scenario(permutated_scene_dict)
            agents_by_distance = sorted(scenario_obj.obstacle_list, key=scenario_obj.tsr_distance_from_ego)
            has_empty_frame = scenario_obj.tsr_distance_from_ego(agents_by_distance[0]) > MAX_LEGAL_DISTANCE_TSRS
            for curr_tsr, next_tsr in zip(agents_by_distance[:-1], agents_by_distance[1:]):
                curr_distance = scenario_obj.tsr_distance_from_ego(curr_tsr)
                next_distance = scenario_obj.tsr_distance_from_ego(next_tsr)
                if next_distance - curr_distance > MAX_LEGAL_DISTANCE_TSRS:
                    assert not has_empty_frame
                    has_empty_frame = True
