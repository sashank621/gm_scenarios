import yaml
import random
import datetime
import json

#TODO: transform this script into a TSR Class with methods that inherits from Actor Class
''' The permutations will be generated in a class structure starting with Actor and diverging
into categories (lanes, tsr, vehicle, etc.) each with field that can be altered and distribution
methods that can be selected for each permutation (uniform, noraml, given input, etc.)
'''

def replace_sign_type_and_yaw(permutation, yaml_to_dict, yaw_change_std):
    """ Find the sign in yaml and replece it according the permutation list
    :param permutation: List with shuffled sign names
    :param yaml_to_dict: loaded yanl file represented in a dict
    :param yaw_change_std: std dev range for yaw permutation [Rad]
    :return:yaml file with signs according the permutation list
    """
    ind = 0
    for item, doc in yaml_to_dict.items():
        if 'agents' in item:
            for agent in doc:
                if 'static_obstacle' in agent.keys():
                    static_obstacle = agent["static_obstacle"]

                    # change sign type
                    costum_model_description = static_obstacle["custom_model_description"]
                    us_sign_configuration = costum_model_description["us_sign_configuration"]
                    us_sign_configuration["type"] = permutation[ind]

                    # change sign yaw
                    state = static_obstacle["initial_state"]
                    pose = state["pose_spec"]
                    rpy = pose["rpy"]
                    rpy["yaw"] = rpy["yaw"]+random.normalvariate(0,yaw_change_std)

                    ind = ind+1
    return yaml_to_dict

def ceate_yaml(input_path, output_path, signs, distribution, num_signs, num_sign_perms, yaw_change_std, num_yaw_perms):
    """function load yaml file and returned yaml file with different raffic signs - according given distribution (in tsr.json)
    :param input_path: yaml input directoey
    :param output_path: yaml output directory
    :param signs: list of sign names
    :param distribution: list of sign relative distribution
    :param num_signs: number of signs for permutation
    :param num_sign_perms: number of sign permutations
    :param yaw_change_std: std range for yaw normal distribution of permutation [Rad]
    :param num_yaw_perms: number of yaw permutations
    :return: void
    """
    with open(input_path) as file:
        yaml_to_dict_input = yaml.full_load(file)

    perm_index=0
    for sign_permutation_index in range(num_sign_perms):

        sign_permutation = random.choices(signs, weights=distribution, k=num_signs)

        for yaw_permutation in range(num_yaw_perms):

            yaml_dict_out = replace_sign_type_and_yaw(sign_permutation, yaml_to_dict_input, yaw_change_std)

            now = datetime.datetime.now()
            with open(output_path + 'route_3_perm-' + str(perm_index) + '_output'+ now.strftime("%Y_%m_%dT%H_%M") + '.scn.yaml', 'w') as fp:
                 yaml.dump(yaml_dict_out, fp)
            print('yaml file created successfully')
            perm_index += 1


def run():
    with open('/home/zzdsfk/projects/uc_workspace/ultracruise/simulated_data_generation_scenarios/scripts/yaml_parsing/tsr.json') as f:
        data = json.load(f)
    ceate_yaml(data['input yaml path'], data['output yaml path'], data['signs'], data['distribution'], data['total signs'], data['num_sign_perms'], data['yaw_change_std'], data['num_yaw_perms'])

if __name__ == "__main__":
    run()

