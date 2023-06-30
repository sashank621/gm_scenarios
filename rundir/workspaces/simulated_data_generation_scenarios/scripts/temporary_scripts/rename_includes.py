import os
import glob


def main():
    base_path = '/home/yzc210/projects/uc_workspace/ultracruise/simulated_data_generation_scenarios/scenarios'
    files = glob.glob(base_path + '/**/*.yaml', recursive=True)
    files = [path for path in files if 'scenarios/old' not in path]
    rename_includes = {
        '- file: scenario://workspace/sim_scenarios/include/vehicle_shape.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/vehicle_shape.inc.yaml',
        '- file: scenario://workspace/sim_scenarios/include/extra_data_noise_config.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/extra_data_noise_config.inc.yaml',
        '- file: scenario://workspace/sim_scenarios/include/uc_channels_MUST_include_spectral_fm.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/uc_channels_MUST_include_spectral_fm.inc.yaml',
        '- file: scenario://workspace/Datagen_TSR_delivery/include/sensor_config_fm_target_v2.0.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sensor_config_fm_target_v2.0.inc.yaml',
        '- file: scenario://workspace/sim_scenarios/include/extra_data_no_uc.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/extra_data_no_uc.inc.yaml',
        '- file: scenario://workspace/Datagen_TSR_delivery/include/local_working_directory_extra_data.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/local_working_directory_extra_data.inc.yaml',
        '- file: scenario://workspace/Datagen_TSR_delivery/delivery_tsr_october/include/sensor_config_fm_target_v1.0.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sensor_config_fm_target_v2.0.inc.yaml',
        '- file: scenario://workspace/Datagen_TSR_delivery/stability_tests/include/sensor_config_fm_stability_new_signs.inc.yaml':
            '- file: scenario://workspace/datagen/stability_tests/include/sensor_config_fm_stability_new_signs.inc.yaml',
        '- file: scenario://workspace/sim_scenarios/include/uc_channels_MUST.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/uc_channels_MUST.inc.yaml',
        '- file: scenario://workspace/sim_scenarios/include/global_vars.inc.yaml':
            '- file: scenario://workspace/datagen/include/target/sim_scenarios/include/global_vars.inc.yaml',
    }
    for path in files:
        with open(path, 'r') as f:
            file_data = f.read()
        for key in rename_includes.keys():
            if key in file_data:
                file_data = file_data.replace(key, rename_includes[key])
        with open(path, 'w') as f:
            f.write(file_data)


if __name__ == '__main__':
    main()
