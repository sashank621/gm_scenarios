import os
from glob import glob


existing = {
        "YIELD_USA_01": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "YIELD_USA_02": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "YIELD_USA_03": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "SPEEDLIMIT_USA_85": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_60": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_70": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_80": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_90": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_100": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_110": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAXKMH_CAD_120": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_40": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_50": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_60": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_70": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_80": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_90": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_100": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        },
        "MAX_CAD_110": {
            "highway_center": [],
            "highway_right": [],
            "urban_center": [],
            "urban_right": [],
        }
    }


def get_scene_names(base_path):
    scene_names = []
    for scene_path in glob(os.path.join(base_path, '*/*/*/*/*/*')):
        scene_names.append(scene_path.split('/')[-1])
    return scene_names


def count_scenes(scene_names):
    for name in scene_names:
        split_name = name.split('_')[:-1]
        index = split_name[1]
        scene = split_name[2]
        lane = split_name[3]
        sign = '_'.join(split_name[5:])
        existing[sign.upper()]['_'.join(split_name[2:4])].append(index)


def check_result():
    missing = []
    for sign_type, sign_value in existing.items():
        for route_key, route_value in sign_value.items():
            for index in range(0, 15):
                if str(index) not in route_value:
                    missing.append('index' + ' '.join([str(index), sign_type, route_key]) + 'is  missing')
    return missing


def main():

    scene_names = get_scene_names('/data/transfer/simulations/tsr_workshop_deliveries/batch_02')
    # scene_names = get_scene_names('/data/transfer/simulations/tsr_workshop_deliveries/batch_02/highway')
    count_scenes(scene_names)
    missing = check_result()
    if not missing:
        print('all good!!')
    else:
        print(missing)



if __name__ == "__main__":
    main()
