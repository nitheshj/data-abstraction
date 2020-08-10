import json
import numpy as np
import sys
import csv
import os

ACTION_START = 2  # no of column from where action names start in csv file;
                # change if the format of data is different in different files
PART1_ID = 0  # no of column used for the user id part 1
PART2_ID = 1  # no of column used for the user id part 2

ACTIONS = {}
STATES = {}
TRAJECTORIES = {}
LINKS = {}

file_names_list = []


def create_node():
    """
    create all the states/nodes for glyph visualization
    :return:
    """
    stateType = 'start'  # start state
    STATES[0] = {
        'id': 0,  # start node has id 0
        'type': stateType,
        'parent_sequence': [],
        'details': {'event_type': 'start'},
        'stat': {},
        'user_ids': []}

    stateType = 'end'  # end state
    STATES[1] = {
        'id': 1,  # end node has id 1
        'parent_sequence': [],
        'type': stateType,
        'details': {'event_type': 'end'},
        'stat': {},
        'user_ids': []}

    stateType = 'mid'
    for action in ACTIONS:
        # print(ACTIONS[action])
        STATES[ACTIONS[action] + 2] = {
            'id': ACTIONS[action] + 2,  # other state has id ranging from 3
            'parent_sequence': [],
            'type': stateType,
            'details': {'event_type': action},
            'stat': {},
            'user_ids': []}


def update_state(state_id, user_id):
    STATES[state_id]['user_ids'].append(user_id)


def add_links(trajectory, user_id):
    """
    adds link between the consecutive nodes of the trajectory
    :param trajectory:
    :param user_id:
    :return:
    """
    for item in range(0, len(trajectory) - 1):
        id = str(trajectory[item]) + "_" + str(trajectory[item + 1])  # id: previous node -> current node
        if id not in LINKS:
            LINKS[id] = {'id': id,
                         'source': trajectory[item],
                         'target': trajectory[item + 1],
                         'user_ids': [user_id]}
        else:
            users = LINKS[id]['user_ids']
            users.append(user_id)
            unique_user_set = list(set(users))
            LINKS[id]['user_ids'] = unique_user_set


def create_trajectory(row, user_id):
    """
    creates trajectory for the given actions of the user
    :param row: the actions of the user
    :param user_id:
    :return:
    """
    trajectory = [0]  # initialize with start state
    action_meaning = ["start_game"]
    key = ""

    update_state(0, user_id)  # update start state with new used id

    action_flag = {}  # keep track which state already have the user id
    for action in ACTIONS:
        action_flag[action] = False

    for item in row:
        if item == "":
            break
        key += ('_'+item)  # generate id for the trajectory
        trajectory.append(ACTIONS[item] + 2)  # append state to the trajectory
        action_meaning.append("transition")  # append action meaning. may use different meaning for different types
                                              # of transition
        if not action_flag[item]:  # check if the user already got to that state before, if so then no need to update
            action_flag[item] = True
            update_state(ACTIONS[item] + 2, user_id)

    # print(key)
    trajectory.append(1)  # end state
    update_state(1, user_id)  # update end state with the new used id
    action_meaning.append("end_game")

    add_links(trajectory, user_id)

    user_ids = [user_id]

    if key in TRAJECTORIES:
        TRAJECTORIES[key]['user_ids'].append(user_id)
    else:
        TRAJECTORIES[key] = {'trajectory': trajectory,
                             'action_meaning': action_meaning,
                             'user_ids': user_ids,
                             'id': key,
                             'completed': True}


def is_start_or_end(state):
    return state['type'] == 'start' or state['type'] == 'end'


def get_state_diff(state1, state2):
    """
        Dependent on action types and raw actions only.
        Return the difference between two states. Each state is represented
        as a 3-tuple involving (stage, action, action parameter)
        
        Skill difference: 10
        Phase difference: 5
        action difference: 1
    """

    # 1. if different stages, it's the max value
    #     if state1[0] != state2[0]:
    #         return state_diff_infinity
    #
    if is_start_or_end(state1) or is_start_or_end(state2):
        if state1 == state2:
            return 0
        else:
            # TO DO state_diff_infinity
            return 100  # TODO infinity

    # 2. No start end involved
    diff = 0
    new_1 = state1['details']['event_type']
    new_2 = state2['details']['event_type']
    # different Activity means different screens: diff is 1
    if new_1 != new_2:
        diff += 1
    # # additional considerations can be done here
    # if (META in state1 and META in state2 and state1[META][ENCOUNTER] == state2[META][ENCOUNTER]) or \
    #     (META not in state1 and META not in state2):
    #     pass
    # else:
    #     diff += 1
    if (new_1[:6] == 'solved' and new_2[:6] != 'solved') or (new_1[:6] != 'solved' and new_2[:6] == 'solved') :
        diff += 1

    if (new_1 == 'solved_safe' and new_2 != 'solved_safe') or (new_1 != 'solved_safe' and new_2 == 'solved_safe'):
        diff += 1

    if (new_1[:11] == 'failed_many' and new_2[:11] != 'failed_many') or (new_1[:11] != 'failed_many' and new_2[:11] == 'failed_many'):
        diff += 3

    if (new_1[:11] == 'failed_once' and new_2[:11] != 'failed_once') or (new_1[:11] != 'failed_once' and new_2[:11] == 'failed_once'):
        diff += 1

    if (new_1 == 'irrelevant_cue' and new_2 != 'irrelevant_cue') or (new_1 != 'irrelevant_cue' and new_2 == 'irrelevant_cue'):
        diff += 2

    if (new_1 == 'no_relevant' and new_2 != 'no_relevant') or (new_1 != 'no_relevant' and new_2 == 'no_relevant'):
        diff += 50

    if (new_1 == 'gave_up' and new_2 != 'gave_up') or (new_1 != 'gave_up' and new_2 == 'gave_up'):
        diff += 80
    #
    if (new_1 == 'gave_up_0' and new_2 != 'gave_up_0') or (new_1 != 'gave_up_0' and new_2 == 'gave_up_0'):
        diff += 1900

    if (new_1 == 'gave_up_1' and new_2 != 'gave_up_1') or (new_1 != 'gave_up_1' and new_2 == 'gave_up_1'):
        diff += 1500

    if (new_1 == 'gave_up_2' and new_2 != 'gave_up_2') or (new_1 != 'gave_up_2' and new_2 == 'gave_up_2'):
        diff += 1100

    if (new_1 == 'gave_up_3' and new_2 != 'gave_up_3') or (new_1 != 'gave_up_3' and new_2 == 'gave_up_3'):
        diff += 650
        
    if (new_1 == 'gave_up_4' and new_2 != 'gave_up_4') or (new_1 != 'gave_up_4' and new_2 == 'gave_up_4'):
        diff += 400

    if (new_1 == 'gave_up_5' and new_2 != 'gave_up_5') or (new_1 != 'gave_up_5' and new_2 == 'gave_up_5'):
        diff += 100

    if (new_1 == 'gave_up_without_trying' and new_2 != 'gave_up_without_trying') or (new_1 != 'gave_up_without_trying' and new_2 == 'gave_up_without_trying'):
        diff += 2100
    #

    return diff


def extract_states(traj):
    """
        Extract state array from trajectory
        trajectory contains only states
    """
    #     return traj.split("_")
    return traj


def TWED(traj1,traj2,stateDict,stateArray,alpha,lamb,normalize = False):
    """
        Compute the Time-Warp Edit distance between two seq/trajectories.

    """

    states1 = extract_states(traj1)
    states2 = extract_states(traj2)

    A_len = len(states1)
    B_len = len(states2)


    A_times = np.arange(A_len)+1
    B_times = np.arange(B_len)+1

    distances = np.zeros((A_len,B_len))


    distances[0:] = sys.maxsize
    distances[:,0] = sys.maxsize
    distances[0,0] = 0


    for i in range(1,A_len):
        for j in range(1,B_len):


            cost_A = get_state_diff(stateDict[stateArray[int(states1[i - 1])]['id']],
                                  stateDict[stateArray[int(states1[i])]['id']])

            delACost =  distances[i-1,j] + cost_A + (alpha * (A_times[i] - A_times[i-1])) + lamb

            cost_B = get_state_diff(stateDict[stateArray[int(states2[j - 1])]['id']],
                                  stateDict[stateArray[int(states2[j])]['id']])

            delBCost = distances[i,j-1] + cost_B + (alpha * (B_times[j]-B_times[j-1])) + lamb

            prevTimeDist = np.abs(A_times[i-1] - B_times[j-1])
            currTimeDist = np.abs(A_times[i] - B_times[j])

            cost_AB_current = get_state_diff(stateDict[stateArray[int(states1[i])]['id']],
                                  stateDict[stateArray[int(states2[j])]['id']])

            cost_AB_prev = get_state_diff(stateDict[stateArray[int(states1[i-1])]['id']],
                                  stateDict[stateArray[int(states2[j-1])]['id']])

            keepCost = distances[i-1,j-1] + cost_AB_current + cost_AB_prev +  (alpha * (prevTimeDist + currTimeDist))

            distances[i,j] = min(delACost,delBCost,keepCost)

    unnormalized = distances[A_len-1,B_len-1]

    if normalize:
        normalized = unnormalized  / (max(A_len,B_len))
        return normalized

    return unnormalized



def compute_dtw(traj1, traj2, stateDict, stateArray):
    """
        Compute DTW of traj1 and traj2
        States are the important factors
        
    """
    states1 = extract_states(traj1)
    states2 = extract_states(traj2)
    #     print 'states1 = %r' %states1
    #     print 'states2 = %r' %states2

    n = len(states1)
    m = len(states2)
    DTW = []
    for i in range(0, n + 1):
        DTW.append([])
        for j in range(0, m + 1):
            DTW[i].append(100)  # TODO state_diff_infinity

    DTW[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = get_state_diff(stateDict[stateArray[int(states1[i - 1])]['id']],
                                  stateDict[stateArray[int(states2[j - 1])]['id']])
            DTW[i][j] = cost + min(DTW[i - 1][j], DTW[i][j - 1], DTW[i - 1][j - 1])

    return DTW[n][m]


def parse_data_to_json_format(csv_reader):
    """
    parse csv data to create node, link and trajectory
    :param csv_reader: raw csv data
    :return:
    """
    create_node()  # create all the states for glyph
    user_count = 0
    user_ids = list()

    for row in csv_reader:
        user_id = row[PART1_ID] + '_' + row[PART2_ID]  # generate user id
        user_ids.append(user_id)
        create_trajectory(row[ACTION_START:len(row)], user_id)

    # generate lists from dictionaries
    state_list = list(STATES.values())
    link_list = list(LINKS.values())
    trajectory_list = list(TRAJECTORIES.values())

    # TO DO sort json_trajectories according to number of users
    json_trajectories = TRAJECTORIES.values()  # sorted(TRAJECTORIES.values(), key=lambda t: len(t['user_ids']), reverse=True)
    # print TRAJECTORIES.values()[0]

    for traj_id, trajectory in enumerate(json_trajectories):
        trajectory['id'] = traj_id

    print "Done!"
    print "Computing traj similarity..." + str(len(json_trajectories))

    # compute traj similarity
    traj_similarity = []

    # traj_id now play the role of similarity ID
    similarity_id = 0

    # skipped_traj_ids stores the trajectories that are too close to some trajectories
    # thus need not be recomputed
    skipped_traj_ids = []

    for i in range(len(json_trajectories) - 1):
        if i not in skipped_traj_ids:
            print "%d," % i,
            assert i == json_trajectories[i]['id']

            for j in range(i + 1, len(json_trajectories)):
                assert j == json_trajectories[j]['id']

                # compID = getDTW_DB_id(i, j, query_setting)

                # simFromDB = dtw_collection.find_one({'_id': compID})
                # if simFromDB is not None:
                #     sim = simFromDB['value']
                # else:
                #     sim = compute_dtw(json_trajectories[i]['trajectory'],
                #                       json_trajectories[j]['trajectory'],
                #                       statespace, state_array)
                #     dtw_collection.insert({'_id': compID, 'value': sim})
                #
                # sim = compute_dtw(json_trajectories[i]['trajectory'],
                #                   json_trajectories[j]['trajectory'],
                #                   STATES, state_list)
                #
                sim = TWED(json_trajectories[i]['trajectory'],
                                  json_trajectories[j]['trajectory'],
                                  STATES, state_list,0.001,1,normalize=True)


                traj_similarity.append({'id': similarity_id,
                                       'source': json_trajectories[i]['id'],
                                       'target': json_trajectories[j]['id'],
                                       'similarity': sim
                                       })
                similarity_id += 1

                # TO DO - How to determine
                similarity_threshold = 0

                if sim < similarity_threshold and j not in skipped_traj_ids:
                    print "Skipping: %d" %j
                    skipped_traj_ids.append(j)

    print "Done!"

    return {'level_info': 'Visualization',
            'num_patterns': user_count,
            'num_users': user_count,
            'nodes': state_list,
            'links': link_list,
            'trajectories': trajectory_list,
            'traj_similarity': traj_similarity,
            'setting': 'test'}


def find_actions(csv_reader):
    """
    finds the action names in the csv file
    :param csv_reader: input file
    :return:
    """
    global ACTIONS
    ACTIONS = {}
    count_action = 0
    for row in csv_reader:
        actions = row[ACTION_START:]

        for item in actions:
            if item == "":
                break
            if item not in ACTIONS:
                ACTIONS[item] = count_action
                count_action += 1


def process_data(raw_data_folder, output_folder, action_from_file=True):
    """
    process each csv file to create the json file for glyph
    :param filename: input csv file
    :param action_from_file: if True then finds the actions names from the file; if False then the actions should be
    manually set in the game_actions variable in main
    :return:
    """

    for subdir, dirs, files in os.walk(raw_data_folder):
        ind = 1
        for filename in files:
            # print (os.path.join(rootdir, file))

            file_base = os.path.basename(filename).split('.')[0]
            ext = os.path.basename(filename).split('.')[1]

            if ext == 'csv':
                print(ind, ":", file_base)
                file_names_list.append(file_base)

                if action_from_file:
                    with open(raw_data_folder+filename, 'r') as data_file:
                        csv_reader = csv.reader(data_file)
                        next(csv_reader, None)
                        find_actions(csv_reader)

                with open(raw_data_folder+filename, 'r') as data_file:
                    csv_reader = csv.reader(data_file)
                    next(csv_reader, None)
                    viz_data = parse_data_to_json_format(csv_reader)
                    with open(output_folder + file_base + '.json', 'w') as outfile:
                        json.dump(viz_data, outfile)
                        outfile.close()

                    print('\tDone writing to : ' + file_base + '.json')

            ind += 1


def create_game_action_dict(actions):
    """
    initializes the dictionary ACTION with the actions and assigns a unique number to each action
    :param actions: a list containing the action names
    :return:
    """
    count_action = 0
    for action in actions:
        ACTIONS[action] = count_action
        count_action += 1


if __name__ == "__main__":
    # manually set actions
    game_actions = \
        [
        #### Old codes    
        # "input_nodes_2",
        # "input_nodes_3",
        # "abstract_symbols",
        # "abstract_symbols_plaque",
        # "safari","buttons","few_dots",
        # "few_dots_plaque","input_nodes_1",
        # "code buttons",
        # "code buttons_safari_True",
        # "code buttons_random_True",
        # "code buttons_nan_False",
        # "safari_plaque","video_safari",
        # "pick_up_plaque","download_stars",
        # "code buttons_hole_True",
        # "download_cypher_directions",
        # "download_cypher_wheel",
        # "code buttons_orb_True",
        # "safe","sticky_note_1"

        ### Stage 01
        # 'video_intro', 'input_nodes_2', 'input_nodes_3', 'buttons',
        #  'many_dots_painting', 'abstract_symbols', 'few_dots', 'input_nodes_1',
        #  'safari', 'code buttons' ,'many_dots_painting_plaque',
        #  'abstract_symbols_plaque' ,'few_dots_plaque', 'puzzle_buttons_nan_False',
        #  'puzzle_buttons_orb_True', 'puzzle_buttons_safari_True', 'all_safari_pics',
        #  'puzzle_buttons_random_True', 'video_safari','safe',
        #  'puzzle_safe_safe_False', 'safari_plaque', 'puzzle_safe_safe_True',
        #  'puzzle_buttons_hole_True', 'puzzle_buttons_glyph_True', 'pick_up_plaque',
        #  'download_stars' 'download_cypher_directions' 'download_cypher_wheel'
        #  'sticky_note_1'

         ### Stage 02 ##########################
        #  'tamagotchi_room','puzzle_bookshelf_bookshelf_True','sticky_note_2',
        #  'video_egg','puzzle_bookshelf_bookshelf_False','egg_table','bookshelf'
        
         ### Stage 03
        # 'download_aris_android', 'download_aris_ios', 'aris_room',
        # 'sticky_note_3', 'video_cyber_garden', 'puzzle_aris_door_aris_door_True',
        # 'aris_projector', 'puzzle_aris_door_aris_door_False', 'aris_door'
        
         ### Stage 04
        # 'main_room', 'desk', 'keypad', 'coffee_table', 'sticky_note_4',
        # 'code keypad', 'tv_guide', 'drawer', 'remote', 'photo_album', 'telegraph_key',
        # 'puzzle_keypad_nan_False', 'download_tv_guide', 'download_tangrams',
        # 'animal_channel', 'pictures', 'puzzle_keypad_0_True', 'channel_1',
        # 'video_animal_channel', 'puzzle_remote_1_True',
        # 'puzzle_telegraph_key_nan_False', 'video_channel_1', 'channel_4',
        # 'puzzle_remote_4_True', 'channel_2', 'channel_7', 'video_channel_4',
        # 'puzzle_remote_2_True', 'video_channel_2', 'channel_5', 'channel_3',
        # 'puzzle_telegraph_key_1_True', 'puzzle_remote_3_True',
        # 'video_telegraph_channel_1', 'video_channel_3',
        # 'puzzle_telegraph_key_5_True', 'video_telegraph_channel_5', 'channel_8',
        # 'puzzle_remote_8_True', 'channel_6', 'channel_9', 'puzzle_remote_5_True',
        # 'video_channel_5', 'puzzle_telegraph_key_8_True',
        # 'video_telegraph_channel_8', 'puzzle_remote_8_False',
        # 'puzzle_remote_6_True', 'video_channel_6', 'puzzle_remote_1_False',
        # 'puzzle_remote_2_False', 'puzzle_remote_5_False', 'puzzle_remote_7_True',
        # 'puzzle_remote_9_False', 'video_channel_8', 'puzzle_remote_9_True',
        # 'puzzle_telegraph_key_2_True', 'video_telegraph_channel_2',
        # 'video_channel_7', 'video_channel_9', 'puzzle_telegraph_key_6_True',
        # 'puzzle_telegraph_key_4_True', 'puzzle_remote_6_False',
        # 'puzzle_remote_3_False', 'puzzle_telegraph_key_3_True',
        # 'video_telegraph_channel_6', 'video_telegraph_channel_4',
        # 'puzzle_remote_4_False', 'video_telegraph_channel_3',
        # 'puzzle_telegraph_key_7_True', 'video_telegraph_channel_7',
        # 'puzzle_telegraph_key_9_True', 'video_telegraph_channel_9',
        # 'puzzle_remote_7_False', 'puzzle_remote_remote_False'
        
        ### Stage 05 
        # 'video_prisoners_dilemma' 'share'

        # I guess change in teams
        # 'input_nodes_2', 'video_intro', 'input_nodes_3', 'buttons',
        # 'many_dots_painting', 'abstract_symbols', 'few_dots', 'input_nodes_1',
        # 'safari', 'code buttons', 'many_dots_painting_plaque',
        # 'abstract_symbols_plaque', 'few_dots_plaque', 'all_safari_pics',
        # 'puzzle_buttons_orb_True', 'puzzle_buttons_nan_False',
        # 'puzzle_buttons_safari_True', 'puzzle_buttons_random_True',
        # 'puzzle_buttons_hole_True', 'video_safari', 'failed_many_times',
        # 'safari_plaque', 'safe', 'puzzle_safe_safe_True', 'puzzle_safe_safe_False',
        # 'pick_up_plaque', 'download_stars', 'download_cypher_directions',
        # 'download_cypher_wheel', 'puzzle_buttons_glyph_True', 'sticky_note_1'

        # Abstraction 01
        # 'navigation',
        # 'irrelevant_cue', 'relevant_cue', 'puzzle_buttons_orb_True',
        # 'puzzle_buttons_nan_False', 'puzzle_buttons_safari_True',
        # 'puzzle_buttons_random_True', 'puzzle_buttons_hole_True',
        # 'failed_many_times', 'puzzle_safe_safe_True', 'puzzle_safe_safe_False',
        # 'puzzle_buttons_glyph_True'

        # Abstraction 02
        'navigation', 'irrelevant_cue', 'relevant_cue', 'no_relevant', 'failed_once',
        'solved_safe', 'solved_safari', 'solved_many_dots', 'solved_glyph',
        'failed_many_times', 'solved_cypher'
        ]

    create_game_action_dict(game_actions)
    # print(ACTIONS)

    raw_data_folder = "data/raw/"
    output_folder = "data/output/"

    process_data(raw_data_folder, output_folder, action_from_file=True)
    # print(ACTIONS)
    # print(STATES)

    # print("File names of visualization_ids.json")
    # print(json.dumps(file_names_list))

    # generate the visualization_ids.json file
    with open(output_folder + 'visualization_ids.json', 'w') as outfile:
        json.dump(file_names_list, outfile)
        outfile.close()
        print("\nvisualization_ids.json file generated.")
