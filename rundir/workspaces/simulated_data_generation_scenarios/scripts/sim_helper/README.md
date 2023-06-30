This executable gives the user a few options (currently 7) to chose from, using a keyboard input.

First 4 options allow the user to observe/edit commonly used files (with "gedit").

The next 2 options allow the user to quickly backup either these commonly used files alongside with datagen scenarios.
Or backup the current working directory to a backup directory in /home/.
The later also saves a log.txt file with the backups made - for traceability.

The last option uses a bash script to patch simian docker when times are rough

______________________________________________________________________________________________

It is recommanded to add this script to bashrc with the following command:
echo "alias sim_helper='bash ~/projects/sim_workspace/ultracruise/simulated_data_generation_scenarios/scripts/sim_helper/sim_helper.sh'" >> ~/.bashrc

______________________________________________________________________________________________

Example of running it:

 =====| EDIT FILE |=====
1. applied_topic_config.json
2. gm_stack_channels_gt_mapping.cc
3. TopicsFactory.cpp
4. sim_configuration.json
 =====| BACKUP |=====
5. backup - applied_topic_config.json & gm_stack_channels_gt_mapping.cc & sim_configuration.json & datagen scenarios
6. backup current working directory
 =====| MISC |=====
7. patch simian

Enter your selection: 



