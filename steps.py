'''
here we will write the declerations of the functions.
than we will source the code to main and use it there
'''

import sys
import os
import pandas as pd
import ast


##### add zone #####

#gets point and return zone.
def get_zone_by_point(point,zones,split_x_to,split_y_to):
    x,y=point
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
    
def add_zone_col(df,pos_col_name,new_pos_col_name,zones,split_x_to,split_y_to):

    #check col_name label exists
    columnsNamesArr = df.columns.values
    listOfColumnNames = list(columnsNamesArr)
    if not pos_col_name in listOfColumnNames:
        print(pos_col_name + "not found in columns.")
        print("use one of those:\n" + listOfColumnNames)
        return()
        
    if  new_pos_col_name in listOfColumnNames:
        print(pos_col_name + "already exists in columns.")
        print("dont one of those:\n" + listOfColumnNames)
        return()
    
    
    for i, row in df.iterrows():
        pos_list = row[pos_col_name] 
        # pos_list=ast.literal_eval(positions_str) needed if its a string.
        
        #pick the first coordinates
        x = pos_list[0]['x']
        y = pos_list[0]['y']
        zone = get_zone_by_point([x,y],zones ,split_x_to,split_y_to)        
        df.at[i,new_pos_col_name] = zone

    return(df)  


##### Team Name #####

def id_to_name(name_df, id, id_col, name_col):
    name_data = name_df[name_df.wyId == id]
    s = name_data[name_col]
    if s.size == 0:
        raise  "nameNotFound"
    name = name_data[name_col].values[0]
    name = name.encode().decode("unicode_escape")  # for latin chars
    return name


def add_team_name(df, id_col, new_col, name_file_path, nf_id_column, nf_name_col):
    #   add_name_by_id.main("step3.csv", "teamId", "team_name", "./raw_data/events_Spain.json", "wyId", "officialName", "stage4.1.csv")

        
    if not os.path.exists(name_file_path):
        print("file "+name_file_path+ " dont exist")
        return()
        
    names_df = pd.read_json(name_file_path)
    
    #check col_name label exists
    columnsNamesArr = df.columns.values
    listOfColumnNames = list(columnsNamesArr)
    if not id_col in listOfColumnNames:
        print(id_col + "not found in columns.")
        print("use one of those:\n" + listOfColumnNames)
        return()
        
    if  new_col in listOfColumnNames:
        print(new_col + "already exists in columns.")
        print("dont one of those:\n" + listOfColumnNames)
        return()
        
    
    df_size=df.size
    for i, row in df.iterrows():
        id=row[id_col]
        name = id_to_name(names_df, id, nf_id_column, nf_name_col)
        #print("Name returnes! "+name )
        if i%10000 == 0:
            print(str(i)+" out of "+str(df_size))

        df.at[i,new_col] = name

    return(df)  
