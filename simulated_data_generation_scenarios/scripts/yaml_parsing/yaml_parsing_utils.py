import math
import numpy as np
import random


def get_truncated_normal_variation_rand(std_deviation, max_deviation):
    while True:
        yaw_permutation_value = random.normalvariate(0, std_deviation)
        if abs(yaw_permutation_value) <= std_deviation:
            break
    return yaw_permutation_value


def wrap_angle_to_pi_range(angle):
    if angle > math.pi:
        while angle > math.pi:
            angle -= 2 * math.pi
    elif angle < math.pi:
        while angle < -math.pi:
            angle += 2 * math.pi
    return angle


def get_orthonormal_base_from_vector(angle_for_base):
    w1 = [np.cos(angle_for_base), np.sin(angle_for_base)]
    w2 = [np.sin(angle_for_base), -np.cos(angle_for_base)]
    return w1, w2


def transform_vector_std_to_angle_base(vector_to_transform, angle_for_base):  # todo change names
    base = get_orthonormal_base_from_vector(angle_for_base)
    new_vector = np.linalg.inv(np.column_stack(base)).dot(vector_to_transform)
    return new_vector


def transform_vector_angle_base_to_std(vector_to_transform, angle_for_base):
    base = get_orthonormal_base_from_vector(angle_for_base)
    new_vector = np.linalg.inv(np.column_stack(base)).dot(vector_to_transform)
    return new_vector


def get_randomized_bool(rate):
    return random.random() < rate
