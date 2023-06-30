import yaml
import random
import datetime
import json


class TSR ():
    def __init__(self,name, dist):
        self. name = name
        self.dist = dist
        self.quant = None


def calc_quant_by_distreb(total,signs):
    """ Update TRS obj with quantity according the given distrebution
    #param: total quantity of signs
    #param: list of TSR() obj
    """
    sum = 0
    for ind, sign in enumerate(signs):
        if ind == len(signs) - 1:
            sign.quant =  total- sum
        else:
            sign.quant = round(sign.dist * total/100)
            sum = sum + sign.quant


def create_distrebuted_signs_vector(signs):
    """Creates a list with 'total' quantity of signs according their distrebution
    :param signs: List of TSR obj
    :return: List of all signs
    """
    dist_signs_vector = []
    dct_all_lists = {}
    for i, sign in enumerate(signs):
        dct_all_lists['lst_%s' % sign.name] = []
        dct_all_lists['lst_%s' % sign.name] = [sign.name] * sign.quant

    for key in dct_all_lists:
        dist_signs_vector.extend(dct_all_lists[key])
    return dist_signs_vector


def create_permutation(dist_signs_vector,num_perms):
    """ Creating a lists as the number of 'num_perm' witch contain random signs order
    :param dist_signs_vector: list of signes with there distrebution - ordered
    :param num_perms: Number of permutations
    :return: List with suffeled sign names
    """
    shuffeled_signs_vector = []
    all_shuffeled_signs_vector = {}
    for perm in range(num_perms):
        all_shuffeled_signs_vector['perm_%s' % perm] = dist_signs_vector[:]
        random.shuffle(all_shuffeled_signs_vector['perm_%s' % perm])
    return all_shuffeled_signs_vector


def replace_sign_type(permutation,yaml_to_dict):
    """ Find the sign in yaml and replece it according the permutation list
    :param permutation: List with sffelef sign names
    :param yaml_to_dict: loaded yanl file represented in a dict
    :return:yaml file with signs according the permutation list
    """
    ind = 0
    for item, doc in yaml_to_dict.items():
        if 'agents' in item:
            for agent in doc:
                if 'static_obstacle' in agent.keys():
                    static_obstacle =agent["static_obstacle"]
                    castom_model_description = static_obstacle["custom_model_description"]
                    us_sign_configuration = castom_model_description["us_sign_configuration"]
                    us_sign_configuration["type"] = permutation[ind]
                    ind = ind+1
    return yaml_to_dict


def ceate_yaml(all_shuffeled_signs_dict, input_path, output_path):
    """function load yaml file and returned yaml file with different raffic signs - according given distrebution (in tsr.json)
    :param all_shuffeled_signs_dict: dictionary of all permutated lists
    :param input_path: yaml input directoey
    :param output_path: yaml output directory
    :return:
    """
    with open(input_path) as file:
        yaml_to_dict_input = yaml.full_load(file)
    for permutation in all_shuffeled_signs_dict.keys():
        yaml_dict_out = replace_sign_type(all_shuffeled_signs_dict[permutation],yaml_to_dict_input)
        now = datetime.datetime.now()
        with open(output_path + permutation + '_output'+ now.strftime("%Y-%m-%d %H:%M") + '.yaml', 'w') as fp:
             yaml.dump(yaml_dict_out, fp)
        print('yaml file created successfully')


def run():
    with open('/home/bzt2gc/projects/uc_workspace/ultracruise/simulated_data_generation_scenarios/src/yaml_parsing/tsr.json') as f:
        data = json.load(f)
    signs = []
    for  sign in zip(data['signs'],data['distrebution']):
        signs.append(TSR(sign[0],sign[1]))
    calc_quant_by_distreb(data['total signs'],signs)
    dist_signs_vector = create_distrebuted_signs_vector(signs)
    all_shuffeled_signs_dict = create_permutation(dist_signs_vector,data["num_perm"])
    ceate_yaml(all_shuffeled_signs_dict, data['input yaml path'],data['outpot yaml path'])

if __name__ == "__main__":
    run()

