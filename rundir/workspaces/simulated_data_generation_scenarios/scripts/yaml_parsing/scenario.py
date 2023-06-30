import copy
import math

from simulated_data_generation_scenarios.scripts.yaml_parsing import static_obstacle
from simulated_data_generation_scenarios.scripts.yaml_parsing import yaml_parsing_utils

GUARANTEED_VIEWING_RANGE = 60

SUPPORTED_WEATHER_PRESETS = {
    'clear': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.1,
                                                'fog_density': 0.01,
                                                'precipitation': 0.0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 110000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.0,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0.0}},
        'weather': 'USER'
    },
    'cloudy': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.32,
                                                'fog_density': 0.01,
                                                'precipitation': 0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 40000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.0,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0}},
        'weather': 'USER'
    },
    'fog_light': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.1,
                                                'fog_density': 0.05,
                                                'precipitation': 0.0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 110000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.0,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0.0}},
        'weather': 'USER'
    },
    'fog_medium': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.1,
                                                'fog_density': 0.1,
                                                'precipitation': 0.0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 110000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.0,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0.0}},
        'weather': 'USER'
    },
    'rain_light': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.2,
                                                'fog_density': 0.01,
                                                'precipitation': 0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 60000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.5,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0}},
        'weather': 'USER'
    },
    'rain_medium': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.32,
                                                'fog_density': 0.01,
                                                'precipitation': 0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 40000},
                                 'world_surface': {'amount_of_driving': 0.0,
                                                   'blend_snow': 0.0,
                                                   'puddle_spread': 0.65,
                                                   'snow_depth': 0.0,
                                                   'water_level': 0.25}},
        'weather': 'USER'
    },
    'snow_light': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.22,
                                                'fog_density': 0.01,
                                                'precipitation': 0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 55000},
                                 'world_surface': {'amount_of_driving': 0,
                                                   'blend_snow': 0.4,
                                                   'puddle_spread': 0,
                                                   'snow_depth': 0.4,
                                                   'water_level': 0}},
        'weather': 'USER'
    },
    'snow_medium': {
        'instance_level_labeling': True,
        'user_defined_weather': {'atmosphere': {'cloud_density': 0.32,
                                                'fog_density': 0.01,
                                                'precipitation': 0,
                                                'scattered_light_scalar': 1.0},
                                 'datetime': {'date': {'day': 21, 'month': 9},
                                              'time_of_day': 1200,
                                              'time_zone': -7.0},
                                 'daylight_savings': {'enable_daylight_savings': False,
                                                      'end_day': 1,
                                                      'end_month': 11,
                                                      'start_day': 8,
                                                      'start_month': 3,
                                                      'switch_hour': 128},
                                 'location': {'lat': 37.0, 'lng': -122.0},
                                 'sun': {'illuminance': 40000},
                                 'world_surface': {'amount_of_driving': 0.5,
                                                   'blend_snow': 0.8,
                                                   'puddle_spread': 0.5,
                                                   'snow_depth': 0.4,
                                                   'water_level': 0.5}},
        'weather': 'USER'
    }
}


class Scenario:
    def __init__(self, scenario_dict):
        self.scenario_dict = scenario_dict
        self.ego_dict = self._extract_ego_dict()
        self.obstacle_list = self._get_obstacle_list()
        self.tsr_amount = len(self.obstacle_list)

    def _extract_ego_dict(self):
        for agent_dict in self.scenario_dict['agents']:
            ego_sub_dict = agent_dict.get('ego')
            if ego_sub_dict:
                return ego_sub_dict
        raise LookupError('Can\'t find ego in source yaml')

    def _get_obstacle_list(self):
        obstacle_list = []
        agent_list = self.scenario_dict['agents']
        for agent_dict in agent_list:
            current_obstacle = static_obstacle.initialize_obstacle(agent_dict)
            if current_obstacle:
                obstacle_list.append(current_obstacle)
        return obstacle_list

    def get_copy(self):
        copy_dict = copy.deepcopy(self.scenario_dict)
        return Scenario(copy_dict)

    def update_scene_name(self, filename: str):
        self.scenario_dict['metadata']['name'] = filename[:-len('.scn.yaml')]

    def set_weather_from_preset(self, preset_name):
        try:
            self.scenario_dict['spectral']['environment'] = SUPPORTED_WEATHER_PRESETS[preset_name]
        except KeyError:
            raise ValueError(f'Do not support preset: \"{preset_name}\"\nOnly support: {SUPPORTED_WEATHER_PRESETS}')

    def dilute_traffic_signs(self, tsr_dilution_rate):
        sorted_traffic_signs = sorted(self.obstacle_list, key=self.tsr_distance_from_ego)
        has_empty_frame = False  # track if potentially empty frame exists in scenario
        included_tsrs = list()
        for tsr_dict in sorted_traffic_signs:
            include_sign = True
            if yaml_parsing_utils.get_randomized_bool(1 - tsr_dilution_rate):  # try to remove from the scene
                if self.other_tsrs_in_frame(tsr_dict, included_tsrs):
                    include_sign = False
                else:  # risk of empty frames
                    if not has_empty_frame:  # first empty frame
                        has_empty_frame = True
                        include_sign = False
            if include_sign:
                included_tsrs.append(tsr_dict)
        included_tsr_ids = {x.obstacle_dict['id'] for x in included_tsrs}
        all_tsr_ids = {i.obstacle_dict['id'] for i in self.obstacle_list}
        discarded_tsr_ids = all_tsr_ids - included_tsr_ids
        for index in discarded_tsr_ids:
            self.remove_traffic_sign(index)

    def remove_traffic_sign(self, agent_id):
        removed_from_list = False
        removed_from_dict = False
        for tsr in self.obstacle_list:
            if tsr.obstacle_dict['id'] == agent_id:
                self.obstacle_list.remove(tsr)
                removed_from_list = True
                break
        for agent in self.scenario_dict['agents']:
            obstacle_data = agent.get('static_obstacle')
            if obstacle_data:
                if static_obstacle.TrafficSign.is_traffic_sign(obstacle_data):
                    if agent['static_obstacle']['id'] == agent_id:
                        self.scenario_dict['agents'].remove(agent)
                        removed_from_dict = True
                        break
        self.tsr_amount -= 1
        if not removed_from_list or not removed_from_dict:
            raise LookupError(f'Requested to remove agent id {agent_id}, but it was not found found')

    def other_tsrs_in_frame(self, tsr_dict, included_tsrs):
        """
        Check if there are any other traffic sign in the visible range behind the given sign
        Returns True also if we are still in the viewing range from ego's starting position
        """
        return self.tsr_distance_from_ego(tsr_dict) <= GUARANTEED_VIEWING_RANGE or \
               any([self.tsr_distance_from_tsr(tsr_dict, other_tsr) <= GUARANTEED_VIEWING_RANGE for other_tsr in
                    included_tsrs])

    def tsr_distance_from_ego(self, tsr: static_obstacle.TrafficSign) -> float:
        tsr_x = tsr.initial_state.pose_spec['px']
        tsr_y = tsr.initial_state.pose_spec['py']
        ego_x = self.ego_dict['initial_position']['point']['utm']['x']
        ego_y = self.ego_dict['initial_position']['point']['utm']['y']
        return math.sqrt(((tsr_x - ego_x) ** 2) + ((tsr_y - ego_y) ** 2))

    @staticmethod
    def tsr_distance_from_tsr(tsr_1: static_obstacle.TrafficSign, tsr_2: static_obstacle.TrafficSign) -> float:
        tsr_1_x = tsr_1.initial_state.pose_spec['px']
        tsr_1_y = tsr_1.initial_state.pose_spec['py']
        tsr_2_x = tsr_2.initial_state.pose_spec['px']
        tsr_2_y = tsr_2.initial_state.pose_spec['py']
        return math.sqrt(((tsr_1_x - tsr_2_x) ** 2) + ((tsr_1_y - tsr_2_y) ** 2))
