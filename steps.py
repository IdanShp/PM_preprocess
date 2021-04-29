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
