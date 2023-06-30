import yaml
import math
import copy

sign_template_dict = {
    'static_obstacle': {
        'custom_model_description': {
            'us_sign_configuration': {
                'type': 'STOP'
            }
        },
        'id': 1,
        'initial_state': {
            'pose_spec': {
                'px': 500011.2043179419,
                'py': 4499994.231589469,
                'rpy': {
                    'pitch': 0,
                    'roll': 0,
                    'yaw': -2.3565926535112261384626433832795
                }
            }
        },
        'model': {
            'static': {
                'height': 1.134,
                'point': [
                    {
                        'x': -0.018,
                        'y': -0.406
                    },
                    {
                        'x': -0.018,
                        'y': 0.406
                    },
                    {
                        'x': 0.018,
                        'y': 0.406
                    },
                    {
                        'x': 0.018,
                        'y': -0.406
                    }
                ]
            }
        },
        'scaling': {
            'x': 1.0,
            'y': 1.0,
            'z': 1.0
        },
        'spectral_static_model': 'CUSTOM_US_SIGN',
        'type': 'UNKNOWN_UNMOVABLE'
    }
}

distance_offset_left_list = [[25, -17], [2, 0], [2, 0], [2, 0], [2, 0],
                             [2, 0], [2, 0], [3, 0], [3, 0], [6, 0],
                             [3, 0], [3, 0], [5, 0], [5, 0], [5, 0],
                             [5, 0], [7, -0.1], [7, -0.1], [7, -0.1], [14, -0.1],
                             [7, 0], [7, 0], [7, 0], [7, 0], [7, 0],
                             [14, 0.2], [7, 0.1], [7, 0.1], [7, 0.1], [7, 0],
                             [7, 0], [14, 0], [7, 0], [7, 0], [7, 0],
                             [7, 0], [7, 0], [14, 0], [7, 0], [7, 0],
                             [7, 0], [7, 0],
                             [7, 0], [7, 0], [7, 0], [7, 0], [7, 0],
                             [7, 0], [7, 0], [7, 0], [7, 0], [7, 0],
                             [7, 0.1], [7, 0.1], [7, 0.1], [7, 0.1], [7, 0.1],
                             [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2],
                             [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2],
                             [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2], [7, 0.2],
                             ]

distance_offset_right_list = [[15, 5], [1.5, 0], [2, 0], [2, 0], [2.5, 0],
                              [3.5, 0], [4, 0], [7, 0], [7, 0], [22, 0],
                              [15, 0], [15, 0], [15, 0], [15, 0], [20, 0],
                              [20, 0], [40, 0], [20, 0], [60, 0], [60, 0],
                              [40, 0.5]
                              ]

BASE_HEADING_RAD = 0.7850000000785671


def generate_x_y_offsets(distance_offset_list, heading_rad):
    result = list()
    for offset_forward, offset_right in distance_offset_list:
        offset_y = offset_forward * math.sin(heading_rad)
        offset_y -= offset_right * math.cos(heading_rad)
        offset_x = offset_forward * math.cos(heading_rad)
        offset_x += offset_right * math.sin(heading_rad)
        result.append((offset_x, offset_y))
    return result


def add_up_offsets(offset_list):
    for i in range(len(offset_list) - 1):
        offset_list[i + 1][0] += offset_list[i][0]
        offset_list[i + 1][1] += offset_list[i][1]


def generate_signs(offset_x_y_list, base_id):
    result = list()
    for index, point in enumerate(offset_x_y_list, start=base_id):
        x_offset = point[0]
        y_offset = point[1]
        next_sign = copy.deepcopy(sign_template_dict)
        next_sign['static_obstacle']['id'] = index
        next_sign['static_obstacle']['initial_state']['pose_spec']['px'] += x_offset
        next_sign['static_obstacle']['initial_state']['pose_spec']['py'] += y_offset
        result.append(next_sign)
    return result


def main():
    ready_signs = list()
    base_id = 1
    for offset_list in [distance_offset_left_list, distance_offset_right_list]:
        add_up_offsets(offset_list)
        offsets_x_y = generate_x_y_offsets(offset_list, BASE_HEADING_RAD)
        ready_signs.extend(generate_signs(offsets_x_y, base_id))
        base_id += len(offset_list)

    final_yaml = {'agents': ready_signs}
    with open('/home/yzc210/tmp/sign_config2.yaml', 'w+') as f:
        yaml.dump(final_yaml, f)


if __name__ == '__main__':
    main()
