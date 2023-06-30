#!/bin/bash

DEFAULT_EDITOR="nano"
KNOWN_EDITORS="vi vim nano gedit"
BACKUP_DIR=~/sim_bckps
SIM_HELPER_ALIAS="sim_helper"
ALIAS_DEST_STR="~/.bash_aliases"

IN_BASHRC=0
CLR_GRN="\e[32m"
CLR_MGN="\e[35m"
CLR_CYN="\e[36m"
CLR_APND="\e[38;5;69m"
CLR_INVLD="\e[38;5;237m"
CLR_RST="\e[0m"
BAD_SLCT_MSG="Invalid selection [!!!]"

# ================= FUNCTIONS =================
ALIAS_DEST=`eval echo "$ALIAS_DEST_STR"`

get_workspace() {
	WORKSPACE=$(pwd | grep "workspace$" | head -1)
	if [ -z "$WORKSPACE" ]; then
		WORKSPACE=$(ls -t ~/projects | grep "workspace$" | head -1)
	fi
}

get_editor() {
	EDITOR=$DEFAULT_EDITOR
	if [[ $1 == "--editor" ]]; then
		if [[ -n $2 && " $KNOWN_EDITORS " == *" $2 "* ]]; then
			EDITOR=$2
		fi
		if [[ -n $3 && " $KNOWN_EDITORS " == *" $3 "* ]]; then
			EDITOR=$3
		fi
	fi
}

get_dir_size() {
	DIR_SIZE=$(du . -sh | awk '{print $1}')
}

alias_exists() {
	local ALIAS_NAME=$1
	local ALIAS_DEST=$2
	#echo "$ALIAS_NAME __ $ALIAS_DEST"
	if [ -f "$ALIAS_DEST" ] && grep -q "alias $ALIAS_NAME=" $ALIAS_DEST; then
		echo "true"
	else
		echo "false"
	fi
}

check_sim_helper_alias() {
	local ax=$(alias_exists $SIM_HELPER_ALIAS $ALIAS_DEST)
	if [ $ax == "true" ]; then
		IN_BASHRC=1
	else
		pad_color_string "_" $CLR_CYN "ALIAS"
		echo "0. add alias to $ALIAS_DEST_STR"
	fi
}

check_alias() {
	local OPT_STR="$1"
	local ALIAS_NAME="$2"
	local RETURN=$3

	local ax=$(alias_exists $ALIAS_NAME $ALIAS_DEST)
	if [ $ax == "true" ]; then
		color_string "$CLR_INVLD" "$OPT_STR (exists)"
		eval $RETURN="exists"
	else
		echo "$OPT_STR"
		eval $RETURN="nope"
	fi
}

option_0() {
	if [ $IN_BASHRC -eq 0 ]; then
		local SIM_HELPER_PATH=$(readlink -f "$0") # path of the current executable
		echo_append "alias $SIM_HELPER_ALIAS='. $SIM_HELPER_PATH --editor $EDITOR'"
		color_string "$CLR_GRN" "Successfuly added the alias to $ALIAS_DEST_STR"
	else
		echo $BAD_SLCT_MSG
	fi
}

make_backup_dir() {
	if [ ! -d "$BACKUP_DIR" ]; then
		mkdir -p $BACKUP_DIR
		echo -e "$CLR_GRN Created backup directory: $BACKUP_DIR $CLR_RST"
	fi
	if [[ -n $1 ]]; then
		mkdir -p "$1"
	fi
}

backup_selected_files() {
	local dir_name=backup_$(date "+%m%d%y_%H%M%S")
	local full_path=$BACKUP_DIR/$dir_name
	local bckup_msg="[$full_path] <- selected files"
	
	make_backup_dir $full_path
	cp $FILE_APLD_TPC_CNFG $FILE_GM_STK_CHNL_MPNG $FILE_SIM_CNFG $full_path
	cp -r ~/projects/$WORKSPACE/ultracruise/simulated_data_generation_scenarios/scenarios $full_path/sim_datagen_scenarios
	
	echo_append "$bckup_msg" "$BACKUP_DIR/backup_log.txt" # Save copy info to a log file for traceability
	color_string $CLR_GRN "Successfuly backed up"
}

backup_current_working_dir() {
	local curr_dir=`pwd`
	local curr_dir_name=$(basename $curr_dir)
	local dir_name=$curr_dir_name\_$(date "+%m%d%y_%H%M%S")
	local full_path=$BACKUP_DIR/$dir_name
	local bckup_msg="[$full_path] <- $curr_dir"
	
	make_backup_dir $full_path
	cp -r $curr_dir/. $full_path
	
	echo_append "$bckup_msg" "$BACKUP_DIR/backup_log.txt" # Save copy info to a log file for traceability
	color_string $CLR_GRN "Successfuly backed up"
}

alias_menu() {
	local choice
	local opt_1 opt_2 opt_3 opt_4
	
	pad_color_string "_" "$CLR_CYN" "ADD ALIAS"
	check_alias "1. nav2*" "nav2uc" opt_1
	check_alias "2. simian_run" "simian_run" opt_2
	check_alias "3. docker_run" "docker_run" opt_3
	check_alias "4. nautilus file explorer" "exp" opt_4
	
	read -p "Enter your selection: " choice
	case $choice in
		1)
			if [ $opt_1 == "exists" ]; then
				echo "Already exists..."
			else
				echo_append "alias nav2uc='cd $UC_DIR'"
				echo_append "alias nav2sim='cd $UC_DIR/simulation'"
				echo_append "alias nav2simulated='cd $UC_DIR/simulated_data_generation_scenarios'"
				echo_append "alias nav2maps='cd $UC_DIR/sim_maps'"
				echo_append "alias nav2datagen_infra='cd $UC_DIR/data_gen_infra'"
				echo_append "alias nav2veh='cd $UC_DIR/vehicle_config'"
				color_string $CLR_GRN "Successfuly added aliases"
			fi
			;;
		2)
			if [ $opt_2 == "exists" ]; then
				echo "Already exists..."
			else
				echo_append "alias simian_run='python3.8 ~/projects/$WORKSPACE/ultracruise/simulation/scripts/launch_simian.py'"
				color_string $CLR_GRN "Successfuly added aliase"
			fi
			;;
		3)
			if [ $opt_3 == "exists" ]; then
				echo "Already exists..."
			else
				echo_append "alias docker_run='. ~/projects/sim_dev_workspace/docker/run_docker.sh'"
				color_string $CLR_GRN "Successfuly added aliase"
			fi
			;;
		4)
			if [ $opt_4 == "exists" ]; then
				echo "Already exists..."
			else
				echo_append "alias exp='nautilus --browser'"
				color_string $CLR_GRN "Successfuly added aliase"
			fi
			;;
		*)
			echo "$BAD_SLCT_MSG"
			;;
	esac
}

color_string() {
	local color=$1
	local string=$2
	echo -e "$color$string$CLR_RST"
}

pad_color_string() {
	local PAD="$1"
	local CLR="$2"
	local STR="$3"
	
	local total_width=30
	local string_length=${#STR}
	local padding_length=$(( (total_width - string_length) / 2 ))
	local left_padding_length=$((padding_length))
	local right_padding_length=$((padding_length))

	if (( (string_length % 2) != 0 )); then
		right_padding_length=$((padding_length + 1))
	fi

	local left_padding=$(printf "%0.s$PAD" $(seq 1 $left_padding_length))
	local right_padding=$(printf "%0.s$PAD" $(seq 1 $right_padding_length))

	local out_str=$(printf "%s| %s |%s" "$left_padding" "$STR" "$right_padding")
	color_string "$CLR" "$out_str"
}

echo_append() {
	local string=$1
	local append_to=$ALIAS_DEST
	if [[ -n $2 ]]; then append_to=$2; fi
	echo -e $CLR_APND
	echo $string | tee -a $append_to
	echo -e $CLR_RST
}
# ================= END FUNCTIONS =================


# ===================== MAIN ======================
get_workspace
get_editor "$@"
get_dir_size

UC_DIR=~/projects/$WORKSPACE/ultracruise
FILE_APLD_TPC_CNFG=$UC_DIR/sim_interface/execution_config/applied_intuition/pubsub/applied_topic_config.json
FILE_GM_STK_CHNL_MPNG=$UC_DIR/simulation/src/uc_sim/gm_applied/interface/gm_stack_channels_gt_mapping.cc
FILE_TPC_FCTRY=$UC_DIR/sim_interface/src/uc_sim/sim_pubsub/factory/src/TopicsFactory.cpp
FILE_SIM_CNFG=$UC_DIR/simulation/sim_configuration.json

# --- Display main menu ---
echo ""
pad_color_string "." $CLR_MGN "$WORKSPACE"
check_sim_helper_alias
pad_color_string "_" $CLR_CYN "$EDITOR/GOTO"
echo "1. applied_topic_config.json"
echo "2. gm_stack_channels_gt_mapping.cc"
echo "3. TopicsFactory.cpp"
echo "4. sim_configuration.json"
pad_color_string "_" $CLR_CYN "BACKUP"
echo "5. #(1, 2, 4) & datagen scenarios"
echo "6. cwd (size: "$DIR_SIZE")"
pad_color_string "_" $CLR_CYN "MISC"
echo "7. patch simian"
echo "8. load build env variables"
echo "9. open alias menu"
echo ""
read -p "Enter your selection: " choice

case $choice in
	0)	# add alias to bashrc
		option_0
		;;
	1)
		# applied_topic_config
		$EDITOR $FILE_APLD_TPC_CNFG
		;;
	"g1")
		cd "$(dirname $FILE_APLD_TPC_CNFG)"
		;;
	2)
		# gm_stack_channels_gt_mapping
		$EDITOR $FILE_GM_STK_CHNL_MPNG
		;;
	"g2")
		cd "$(dirname $FILE_GM_STK_CHNL_MPNG)"
		;;
	3)
		# TopicsFactory
		$EDITOR $FILE_TPC_FCTRY
		;;
	"g3")
		cd "$(dirname $FILE_TPC_FCTRY)"
		;;
	4)
		# sim_configuration
		$EDITOR $FILE_SIM_CNFG
		;;
	"g4")
		cd "$(dirname $FILE_SIM_CNFG)"
		;;
	5)
		# backup - applied_topic_config & gm_stack_channels_gt_mapping & sim_configuration.json
		backup_selected_files
		;;
	6)
		# backup cwd
		backup_current_working_dir
		;;
	7)
		# patch simian
		bash $UC_DIR/simulation/scripts/simian_docker_workaround/patch_simian.sh
		;;
	8)
		if ! grep -sq 'docker\|lxc' /proc/1/cgroup; then
		   echo "Please run inside a docker container."
		else
			source $UC_DIR/build.sh -project-name UC_PROJECT_SIM_ULTRACRUISE -r -sim -install -e
		fi
		;;
	9)
		alias_menu
		;;

	*)
		echo $BAD_SLCT_MSG
		;;
esac
# ===================== END MAIN ======================
