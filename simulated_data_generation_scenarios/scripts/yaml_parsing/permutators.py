import random
from simulated_data_generation_scenarios.scripts.yaml_parsing import yaml_parsing_utils
from simulated_data_generation_scenarios.scripts.yaml_parsing.scenario import Scenario
from simulated_data_generation_scenarios.scripts.yaml_parsing.static_obstacle import TrafficSign


class SignTypePerm:
    def __init__(self, sign_type_dict, total_number_of_signs):
        self.permutate = sign_type_dict is not None
        if self.permutate:
            self.type_distribution_dict = sign_type_dict.get('sign_type_dist')
            if not self.type_distribution_dict:
                raise ValueError('Sign face permutation is requested but no distribution is specified')
            self.total_number_of_signs = total_number_of_signs
            self._sign_face_pool = self._get_face_pool()

    def apply_permutation(self, scene: Scenario):
        if not self.permutate:
            return
        for obstacle in scene.obstacle_list:
            if isinstance(obstacle, TrafficSign):
                obstacle.set_sign_type(self._get_single_sign_face())

    def _get_single_sign_face(self):
        return self._sign_face_pool.pop(random.randint(0, len(self._sign_face_pool) - 1))  # randint bounds inclusive

    def _get_face_pool(self):
        face_pool = list()
        sum_weights = sum(self.type_distribution_dict.values())
        instance_weight_ratio = self.total_number_of_signs / sum_weights
        for sign_type, sign_weight in self.type_distribution_dict.items():
            face_pool.extend([sign_type] * int(sign_weight * instance_weight_ratio))
        while len(face_pool) < self.total_number_of_signs:  # make sure we have enough sign instances
            face_pool.append(random.choice(face_pool))  # increase count of random face
        return face_pool


class SignYawPerm:
    def __init__(self, sign_yaw_dict):
        self.permutate = sign_yaw_dict is not None
        if self.permutate:
            self._std_deviation = sign_yaw_dict.get('yaw_change_std')
            self._max_deviation = sign_yaw_dict.get('yaw_change_max')
            if not all((self._std_deviation, self._max_deviation)):
                raise LookupError('Corrupt sign yaw configuration dict!!')

    def apply_permutation(self, scene: Scenario):
        if not self.permutate:
            return
        for obstacle in scene.obstacle_list:
            if isinstance(obstacle, TrafficSign):
                curr_yaw = obstacle.initial_state.pose_spec['rpy']['yaw']
                yaw_offset = yaml_parsing_utils.get_truncated_normal_variation_rand(self._std_deviation,
                                                                                    self._max_deviation)
                obstacle.set_yaw(curr_yaw + yaw_offset)


class PostHeightPerm:
    def __init__(self, post_height_dict, total_number_of_signs):
        self.permutate = post_height_dict is not None
        if self.permutate:
            self.post_distribution_dict = post_height_dict
            self.total_number_of_signs = total_number_of_signs
            self._sign_post_pool = self._generate_weighted_post_list()

    def _generate_weighted_post_list(self):
        post_pool = list()
        sum_weights = sum(self.post_distribution_dict.values())
        instance_weight_ratio = self.total_number_of_signs / sum_weights
        for height, weight in self.post_distribution_dict.items():
            post_pool.extend([height] * int(weight * instance_weight_ratio))
        while len(post_pool) < self.total_number_of_signs:  # make sure we have enough sign instances
            post_pool.append(random.choice(post_pool))
        if self.permutate and not post_pool:
            raise ValueError('Post height requested, but no description given!!')
        return post_pool

    def _get_random_post_height(self):
        return self._sign_post_pool.pop(random.randint(0, len(self._sign_post_pool) - 1))  # randint bounds inclusive

    def apply_permutation(self, scene: Scenario):
        if not self.permutate:
            return
        for obstacle in scene.obstacle_list:
            if isinstance(obstacle, TrafficSign):
                obstacle.set_post_height(self._get_random_post_height())
