import abc
import random
from simulated_data_generation_scenarios.scripts.yaml_parsing import yaml_parsing_utils

NORMAL_SIGNS = [
    'STOP_USA_CAD',
    'YIELD_USA_01',
    'YIELD_USA_02',
    'YIELD_USA_03',
    'AXLEWEIGHTLIMITTONS_USA',
    'CURVESPEEDKMH_USA',
    'CURVESPEEDMPH_USA',
    'EXITMPH2_USA',
    'EXITMPH_USA',
    'EXITNUMBER_USA',
    'EXITSPEEDMPH_USA',
    'MAXIMUMTONS_USA',
    'MAXMPHORANGE_USA',
    'MAXMPH_USA_YELLOW',
    'MINIMUMSPEEDKMH_USA',
    'MINIMUMSPEED_USA',
    'MINIMUM_CAD',
    'RAMPMPH_USA',
    'SPEEDLIMITUPCOMING_USA_01',
    'SPEEDZONEAHEADMPH_USA_01',
    'WEIGHTLIMITTONS_USA',
    'TRUCKSMAXSPEED_USA',
    'TRUCKSKMH_USA',
]

SPEED_LIMIT_SIGNS = [
    'SPEEDLIMIT_USA',
    'MAXKMH_CAD',
    'MAX_CAD',
    'MAXKMH_CAD_BLACK_01'
]

MULTI_SIGNS = [
    'REDUCEDSPEED_USA',
    'SCHOOLSPEEDLIMITDURINGRESTRICTEDHOURS_USA',
    'SCHOOLZONEMPHWHENFLASHING_USA',
]

FALSE_ALARM_SIGNS = [
    'AXLEWEIGHTLIMITTONS_USA',
    'CURVESPEEDKMH_USA',
    'CURVESPEEDMPH_USA',
    'EXITMPH2_USA',
    'EXITMPH_USA',
    'EXITNUMBER_USA',
    'EXITSPEEDMPH_USA',
    'MAXIMUMTONS_USA',
    'MAXMPHORANGE_USA',
    'MAXMPH_USA_YELLOW',
    'MINIMUMSPEEDKMH_USA',
    'MINIMUMSPEED_USA',
    'MINIMUM_CAD',
    'RAMPMPH_USA',
    'SPEEDLIMITUPCOMING_USA_01',
    'SPEEDZONEAHEADMPH_USA_01',
    'WEIGHTLIMITTONS_USA',
    'REDUCEDSPEED_USA',
    'REDUCEDSPEED_USA:CITYWIDE_USA',
    'REDUCEDSPEED_USA:NEIGHBORHOOD_USA',
    'REDUCEDSPEED_USA:RESIDENTIAL_USA',
    'SCHOOLSPEEDLIMITDURINGRESTRICTEDHOURS_USA',
    'SCHOOLZONEMPHWHENFLASHING_USA',
    'TRUCKSMAXSPEED_USA',
    'TRUCKSKMH_USA',
]


SUPPORTED_SIGNS = NORMAL_SIGNS + SPEED_LIMIT_SIGNS + MULTI_SIGNS

DEFAULT_POST = 'MESH_7_5FT'

SIGN_WEAR_TYPES = [
    'cracking_amount',
    'dirt_amount',
    'rust_amount',
    'peeling_amount'
]


class InitialState:
    def __init__(self, initial_state_dict):
        self.pose_spec = initial_state_dict['pose_spec']


class ModelDescription:
    def __init__(self, custom_model_description: dict):
        self.sign_configuration = _get_actor_class(custom_model_description)

    @staticmethod
    def _get_sign_configuration(custom_model_description: dict):
        sign_configuration = custom_model_description.get('sign_configuration')
        if sign_configuration:
            return sign_configuration
        else:
            raise ValueError('Missing obstacle\'s \"sign_configuration\"')


class StaticObstacle(abc.ABC):
    def __init__(self, initial_state_dict):
        self.obstacle_dict = initial_state_dict
        self.initial_state = InitialState(initial_state_dict['initial_state'])

    @abc.abstractmethod
    def set_yaw(self, yaw):
        pass


class TrafficSign(StaticObstacle):
    def __init__(self, agent_data: dict):
        super().__init__(agent_data)
        self.model_description = self._get_model_description(agent_data)

    @staticmethod
    def is_traffic_sign(agent_data: dict):
        spectral_static_model = agent_data.get('spectral_static_model')
        if spectral_static_model:
            if spectral_static_model == 'CUSTOM_US_SIGN' or spectral_static_model == 'CUSTOM_SIGN':
                return True
        return False

    @staticmethod
    def is_speed_limit(preset):
        return preset in SPEED_LIMIT_SIGNS

    @staticmethod
    def _get_model_description(agent_data: dict) -> dict:
        spectral_static_model = agent_data.get('spectral_static_model')
        if spectral_static_model == 'CUSTOM_SIGN':
            custom_model_description = agent_data.get('custom_model_description')
            if custom_model_description:
                if custom_model_description.get('sign_configuration'):
                    return custom_model_description
                else:
                    raise ValueError('Missing obstacle\'s \"sign_configuration\"')
            else:
                raise ValueError('Missing obstacle\'s \"custom_model_description\"')
        elif spectral_static_model:
            raise NotImplementedError('Only \"CUSTOM_SIGN\" spectral static model is supported')
        else:
            raise ValueError('Missing obstacle\'s \"spectral_static_model\"')

    def set_sign_type(self, sign_description: str):
        sign_configuration = self.model_description['sign_configuration']
        sign_configuration.pop('preset', None)
        sign_configuration.pop('maximum_speed', None)
        sign_configuration.pop('boards', None)
        split_description = sign_description.split(':')
        preset = split_description.pop(0)
        if preset not in SUPPORTED_SIGNS:
            raise NotImplementedError(f'Sign type \"{preset}\" is not supported')
        sign_configuration['preset'] = preset
        if preset in SPEED_LIMIT_SIGNS:
            sign_configuration.update(self._get_speed_limit_fields(preset, split_description))
        if preset in FALSE_ALARM_SIGNS:
            sign_configuration.update(self._get_false_alarm_speed_value(preset))
        if preset in MULTI_SIGNS:
            sign_configuration.update(self._get_multi_sign_fields(preset, split_description))
        self.model_description['sign_configuration'] = sign_configuration

    def set_yaw(self, yaw):
        self.initial_state.pose_spec['rpy']['yaw'] = yaw

    def set_wear(self, wear_value):
        self.model_description['sign_configuration']['material'] = {
            random.choice(SIGN_WEAR_TYPES): wear_value
        }

    def set_post_height(self, post_height_description):
        self.model_description['sign_configuration']['post'] = post_height_description

    @staticmethod
    def _get_speed_limit_fields(preset, split_description):
        fields = dict()
        maximum_speed = split_description.pop(0)
        if not maximum_speed:
            raise ValueError(f'Missing maximum speed for type {preset}')
        fields['maximum_speed'] = int(maximum_speed)
        return fields

    @staticmethod
    def _get_multi_sign_fields(preset, split_description):
        fields = dict()
        if preset == 'REDUCEDSPEED_USA':
            if split_description:
                additional_board = split_description.pop(0)
                if additional_board == 'CITYWIDE_USA':
                    fields['boards'] = [{
                        'model': 'CITYWIDE_USA',
                        'where': 'BELOW'
                    }]
                elif additional_board == 'NEIGHBORHOOD_USA':
                    fields['boards'] = [{
                        'model': 'NEIGHBORHOOD_USA',
                        'where': 'BELOW'
                    }]
                elif additional_board == 'RESIDENTIAL_USA':
                    fields['boards'] = [{
                        'model': 'RESIDENTIAL_USA',
                        'where': 'BELOW'
                    }]
                else:
                    raise ValueError(f'Error! Preset: {preset} does not support additional board: {additional_board}')
        elif preset == 'SCHOOLSPEEDLIMITDURINGRESTRICTEDHOURS_USA':
            pass  # todo add option for flashing lights and restricted hours once supported in sim
        elif preset == 'SCHOOLZONEMPHWHENFLASHING_USA':
            pass  # todo add option for flashing lights once supported in sim

        if split_description:
            raise ValueError(f'Error! For preset {preset}, there was left unused description part {split_description}')

        return fields

    @staticmethod
    def _get_false_alarm_speed_value(preset):
        fields = dict()
        maximum_speed = random.randrange(25, 65 + 1, 5)
        if not maximum_speed:
            raise ValueError(f'Missing maximum speed for type {preset}')
        fields['maximum_speed'] = int(maximum_speed)
        return fields


def initialize_obstacle(agent_dict):
    for header, agent_data in agent_dict.items():
        if header == 'ego':
            return None
        if header == 'static_obstacle':
            obstacle = agent_data
            break
    else:
        raise NotImplementedError('No TSRs found')

    obstacle_class = _get_actor_class(agent_data)
    return obstacle_class(agent_data)


def _get_actor_class(agent_data: dict):
    if TrafficSign.is_traffic_sign(agent_data):
        return TrafficSign
    else:
        raise NotImplementedError('Currently only supports TSRs')
