'''
here we will write the declerations of the functions.
than we will source the code to main and use it there
'''

from datetime import timedelta
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



def assign_case_id(events_df, caseid_col, team_id_col,match_id_col, trace_team_id,max_distance):
    
    case_id=0
    dist=0
    prev_game=""
    #for each row
    for i, row in events_df.iterrows():
        if prev_game!=events_df.at[i, match_id_col]:
            prev_game=events_df.at[i, match_id_col]
            case_id+=1
            dist=0
        team_id=events_df.at[i, team_id_col]
        if team_id == trace_team_id:
            if dist > max_distance:
                case_id+=1
                dist=0
            events_df.at[i, caseid_col] = case_id
        
        else:
            dist+=1

        
    return events_df


    

def get_2d_cases(events_df, caseid_col, team_name_col, team_id_col, tags_col, event_col,zone_col):
    case_id = 1
    current_case_used = True
    high_value_cases = []

    for i, row in events_df.iterrows():
        team_name=row[team_name_col]
        tags = row[tags_col]
        if team_name == 'Barcelona' and ((1801 in tags or 703 in tags) or 'Shot' in row['eventName']):
            events_df.at[i, caseid_col] = str(case_id)
            #print("CaseID given "+ str(case_id))
            current_case_used = True
            # if frame not in ['D1', 'D2', 'D3'] and str(case_id) not in low_value_cases:
            if ('Shot' in row[event_col] or row[zone_col] == 'D2') and str(case_id) not in high_value_cases:
                high_value_cases.append(str(case_id))
                #print(high_value_cases)
            # print(str(case_id))
        elif team_name != 'Barcelona' and row[event_col] == 'Dual' and 701 in tags:
            events_df.at[i, caseid_col] = 0
        else:
            if current_case_used:
                case_id += 1
                current_case_used = False
            events_df.at[i, caseid_col] = 0
        
    # print(high_value_cases)
    new_items_df = events_df.loc[events_df[caseid_col].isin(high_value_cases)].copy()
    return(new_items_df)


def half_to_90min(df,halfs_col="matchPeriod" ,seconds_col="eventSec" ):
    for i, row in df.iterrows():
        event_sec = row[seconds_col]
        event_half = row[halfs_col]
        if event_half == '2H':
            event_sec += 2700
        df.at[i,seconds_col] = event_sec

    return df



def remove_loops(df, player_col, case_id_col, seconds_col="eventSec"):
    
    #create new d ataframe with same columns
    columns_list = list(df.columns.values)
    new_df=pd.DataFrame(columns=columns_list)

    # for each row, check if its the same case_if
    df_index=df.index
    j=0
    
    for i in range(1,len(df.index)):
        #if same case id
        if df.at[df_index[i],case_id_col] != df.at[df_index[j],case_id_col] or df.at[df_index[i],player_col] != df.at[df_index[j],player_col]:
            #add row to new df
            new_df=new_df.append([ df.loc[df_index[j]] ])

            # get time from prev row
            new_df.at[df_index[j], "end_time"] = df.at[df_index[i-1],seconds_col]
            j=i
    return new_df
           



# add dates
def add_date(df,time_col,match_col,date_col,begin_date,time_between):
    """
    adding date columns to the game
    df - the dataframe
    begin date - date of the fisrst game
    time_between - time between games
    """
    main_timer=begin_date
    events_ids=list(iter(df.index))
    current_match=df.at[events_ids[0],match_col]
    for i, row in df.iterrows():
        if current_match != df.at[i,match_col]:
            main_timer+=time_between
        df.at[i,date_col]=str(main_timer+timedelta(seconds=df.at[i,time_col]))
    return(df)
        

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
