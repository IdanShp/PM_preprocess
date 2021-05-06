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


def get_2d_cases(events_df):
    case_id = 1
    current_case_used = True
    high_value_cases = []

    for i, row in events_df.iterrows():
        team_name=row["team_name"]
        tags = row["tags"]
        if team_name == 'Barcelona' and ((1801 in tags or 703 in tags) or 'Shot' in row['eventName']):
            events_df.at[i, 'caseId'] = str(case_id)
            #print("CaseID given "+ str(case_id))
            current_case_used = True
            # if frame not in ['D1', 'D2', 'D3'] and str(case_id) not in low_value_cases:
            if ('Shot' in row['eventName'] or row["zone"] == 'D2') and str(case_id) not in high_value_cases:
                high_value_cases.append(str(case_id))
                #print(high_value_cases)
            # print(str(case_id))
        elif team_name != 'FC Barcelona' and row['eventName'] == 'Dual' and 701 in tags:
            events_df.at[i, 'caseId'] = 0
        else:
            if current_case_used:
                case_id += 1
                current_case_used = False
            events_df.at[i, 'caseId'] = 0
        
    print(high_value_cases)
    new_items_df = events_df.loc[events_df['caseId'].isin(high_value_cases)].copy()
    return(new_items_df)


def remove_loops(df, col_name, case_id_col):
    columnsNamesArr = df.columns.values
    listOfColumnNames = list(columnsNamesArr)
    if not col_name in listOfColumnNames:
        print(col_name + "not found in columns.")
        print("use one of those:\n" + str(listOfColumnNames))
        return
    

    try:
        i=0
        prev_case_id=""
        events_ids=list(iter(df.index))
        while i:
            #if new  case:
            if prev_case_id != df.at[events_ids[i],"caseId"]:
                prev_case_id=df.at[events_ids[i],"caseId"]
                start_event_idx=i
                
                #TODO: start_time?
                end_time=df.at[events_ids[i],"relEventTime"]
                
            else:
                # look for new col_name value or new caseID
                while ((i < df.size) & (prev_case_id==df.at[events_ids[i],"caseId"]) & 
                       (df.at[events_ids[i],col_name]==df.at[start_event_idx,col_name])):
                    end_time=df.at[events_ids[i],"relEventTime"]
                    next(i)
                df.at[start_event_idx,"end_time"] = end_time
                #TODO: copy the row to a new df (or filter at the end of it.)
                
                start_event_idx=i
                end_time=df.at[events_ids[i],"relEventTime"]
                
            next(i)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("while i=" + str(i) + "size of df is "+str(df.size))
        raise
    
    df = df.dropna()
    return df

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
