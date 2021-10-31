import pandas as pd
import configurations as conf

print("reloading last case_id")
normal=pd.read_json(conf.json_names["caseid_file"], orient='index', **conf.read_json_args)
good=pd.read_json(conf.json_names["good_caseid_file"], orient='index', **conf.read_json_args)
bad=pd.read_json(conf.json_names["bad_caseid_file"], orient='index', **conf.read_json_args)

zone_normal=pd.read_json(conf.json_names["zone_caseid_file"], orient='index', **conf.read_json_args)
zone_good=pd.read_json(conf.json_names["zone_good_caseid_file"], orient='index', **conf.read_json_args)
zone_bad=pd.read_json(conf.json_names["zone_bad_caseid_file"], orient='index', **conf.read_json_args)


df_list=[normal,good,bad,zone_normal,zone_good,zone_bad]
for df in df_list:
        
    # get players of the team. need to be a list with index() function
    players_list = sorted(list(df[conf.eventsfile_pname].unique()))
    

    # create matrix of size players.len x players.len
    directly_matrix=[]
    dependency_matrix=[]
    for i in range(len(players_list)):
        directly_matrix.append([0]*len(players_list))
    for i in range(len(players_list)):
        dependency_matrix.append([0]*len(players_list))



    prev_row=[]
    prev_player=""
    prev_case=-1
    i=1

    # calc directly follows
    for i, row in df.iterrows():
        current_player=row[conf.eventsfile_pname]
        current_case=row[conf.case_id_col]
        if current_case == prev_case:
            directly_matrix[players_list.index(prev_player)][players_list.index(current_player)] += 1
        prev_player=current_player
        prev_case=current_case

    # calc dependency
    for i in range(len(players_list)):
        for j in range(len(players_list)):
            numerator = (directly_matrix[i][j] - directly_matrix[j][i]) if (i != j) else (directly_matrix[i][j])
            denominator = (directly_matrix[i][j] + directly_matrix[j][i] + 1) if (i != j) else (directly_matrix[i][j] + 1)
            dependency_matrix[i][j] = numerator / denominator

    print("done with ", i)
    i+=1
   


# translate to dataframe:
    directly_follows_df = pd.DataFrame(directly_matrix, columns=players_list, index=players_list)
    dependency_df = pd.DataFrame(dependency_matrix, columns=players_list, index=players_list)

    # TODO: save it to file before goind to the next dataframe

    break


