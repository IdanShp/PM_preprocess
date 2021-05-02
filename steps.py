'''
here we will write the declerations of the functions.
than we will source the code to main and use it there
'''

import sys
import os
import pandas as pd
import ast


##### add zone #####

# gets point and return zone.
def get_zone_by_point(point, zones, split_x_to, split_y_to):
    x, y = point
    seg_x = 0
    seg_y = 0
    for i, segment_len in enumerate(split_x_to):
        seg_x += segment_len
        if y < seg_x:
            break

    for j, segment_len in enumerate(split_y_to):
        seg_y += segment_len
        if x < seg_y:
            break
    zone = zones[j][i]
    return zone


def add_zone_col(df, pos_col_name, new_pos_col_name, zones, split_x_to, split_y_to):
    # check col_name label exists
    columnsNamesArr = df.columns.values
    listOfColumnNames = list(columnsNamesArr)
    if not pos_col_name in listOfColumnNames:
        print(pos_col_name + "not found in columns.")
        print("use one of those:\n" + listOfColumnNames)
        return ()

    if new_pos_col_name in listOfColumnNames:
        print(pos_col_name + "already exists in columns.")
        print("dont one of those:\n" + listOfColumnNames)
        return ()

    for i, row in df.iterrows():
        pos_list = row[pos_col_name]
        # pos_list=ast.literal_eval(positions_str) needed if its a string.

        # pick the first coordinates
        x = pos_list[0]['x']
        y = pos_list[0]['y']
        zone = get_zone_by_point([x, y], zones, split_x_to, split_y_to)
        df.at[i, new_pos_col_name] = zone

    return (df)


##### Team Name #####

def add_team_name(df, id_col, new_col, name_file_path, nf_id_column, nf_name_col):
    # add_name_by_id.main("step3.csv", "teamId", "team_name", "./raw_data/events_Spain.json", "wyId", "officialName", "stage4.1.csv")

    if not os.path.exists(name_file_path):
        print("file " + name_file_path + " dont exist")
        return ()

    names_df = pd.read_json(name_file_path)

    # check col_name label exists
    columnsNamesArr = df.columns.values
    listOfColumnNames = list(columnsNamesArr)
    if not id_col in listOfColumnNames:
        print(id_col + "not found in columns.")
        print("use one of those:\n" + listOfColumnNames)
        return ()

    if new_col in listOfColumnNames:
        print(new_col + "already exists in columns.")
        print("dont one of those:\n" + listOfColumnNames)
        return ()

    # make dic from df
    names_id = names_df.set_index(nf_id_column).to_dict('index')

    df_size = df.size
    for i, row in df.iterrows():
        id = row[id_col]
        name = names_id[id][nf_name_col]
        if len(name) == 0:
            name = "ID" + str(id)
        if i % 10000 == 0:
            print(str(i) + " out of " + str(df_size))

        df.at[i, new_col] = name

    return (df)

# steps:
# filter season with wanted matches (by match id in config file)
# open filtered json as dataframe

# convert tags from dict to list
# read player id, add player name column
# read team id, add team name column
# match id - do nothing
# read position (coordinates) and convert to frame
# consider - event second, match half and last game finish time. calculate event absolute time and relative time
# save file

# open file
# set case ID by - team name, tags, event name.
# save file

# open file
# filter High value cases
# filter short moves (optional)
# save file

# open file
# add trace start and end states (optional)
# save file
