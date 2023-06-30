#!/bin/bash

AFFINITY_FILE=$HOME"/projects/uc_workspace/ultracruise/application/scripts/tasksetAffinity"
SPECTRAL_VERSION=$( cat < $HOME"/projects/uc_workspace/ultracruise/simulated_data_generation_scenarios/scripts/spectral_version_contros.txt" )
cont_name="uc-develop-2.8.2-"$USER

: '
function set_affinity {
  CPU_CORES=$(nproc)
  CONFIG="sim"

  if [ ${CPU_CORES} -lt 12 ]; then
    CONFIG="sim8"
  fi

  source ${AFFINITY_FILE}
  set_affinity $CONFIG
  SIM_AFFINITY=$(get_affinity "simulation")
  echo $SIM_AFFINITY
}

affinity_cores=$(set_affinity)
'


spectral_container_name="gm-spectral"
if [ "$( docker container inspect -f '{{.State.Status}}' $spectral_container_name )" != "running" ]; 
then
    echo "Launching gm-spectral docker"
    echo "`/bin/bash $HOME/AI/gm_applied/datagen_interface/docker/start.sh --copy_bag_to /data/transfer/simulations/bag_output_$USER`"
else
    echo "gm-spectral container already running"
fi


echo "Launching Spectral"
running_dir=$HOME"/AI/"$SPECTRAL_VERSION
echo
cd $running_dir
echo "
current_workspace: local
workspace:
- name: local
  maps: maps
  scenarios: $HOME/projects/uc_workspace/ultracruise/simulated_data_generation_scenarios/scenarios
  output: output/
  input_drives: input/drives/
  input_maps: input/maps/
  input_models: input/models/
  frontend: frontend/
  db: database/
  container_name: gm_simian_interface
  config: config.yaml" > datagen_workspace.yaml

echo "
default_simulation_flags: --sensor_port_adjust --container_name=gm-spectral --v2api
plugin_configs:
- server_run_cmd: \"PYTHONPATH=$HOME/projects/uc_workspace/ultracruise/build/lib/python2.7/site-packages:/opt/ros/melodic/install/lib/python3/dist-packages:/opt/sumo/tools:$HOME/projects/uc_workspace:$HOME/projects/uc_workspace/ultracruise:$HOME/projects/uc_workspace/ultracruise/simulation/src/simulation:$HOME/projects/uc_workspace/ultracruise/build:$HOME/projects/uc_workspace/ultracruise/build/lib/:$HOME/projects/uc_workspace/ultracruise/build_prototype_release/:$HOME/projects/uc_workspace/ultracruise/build_prototype_debug/ python2 $HOME/projects/uc_workspace/ultracruise/simulation/resources/simian/gm_plugins/gm_plugin_service.py\"
  port: 10017
  name: python_server
  container_username: \"$(id -u)\"
  container_name: $cont_name "> config.yaml




# python3 ./simian.par  --workspace_file datagen_workspace.yaml  --simulation_flags="--sensor_port_adjust --container_name=gm-spectral --sensor_sim"

python3 ./simian.par --workspace_file datagen_workspace.yaml
#echo "
#default_simulation_flags: "--sensor_port_adjust --container_name=gm-spectral --sensor_sim" "> config.yaml
#python2 ./simian.par --workspace_file=datagen_workspace.yaml 

cd - 
