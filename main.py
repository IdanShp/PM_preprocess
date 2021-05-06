import os
import sys
import pandas as pd


CREATE_NEW_DATASET = True

# time for monitoring
import time

# TODO give an option to create everything again

# 0.load configuration
import configurations as conf
# source steps file. (import steps as ...)
import steps as step

start_time = time.process_time()

if 'CREATE_NEW_DATASET' in locals() or not os.path.exists(conf.prepare_file):
    print("creating new data_set")

    # 1.prepare files
    # unzip (if necessary)
    already_unzipped = 1
    for f in [conf.events_file, conf.players_file, conf.teams_file, conf.matches_file]:
        if not os.path.exists(f):
            already_unzipped = 0
            break

    if not already_unzipped:
        print("extracting files from zip")
        import zipfile

        with zipfile.ZipFile(conf.resources_arch, 'r') as zip_ref:
            zip_ref.extractall(conf.resources_dir)

    # 2.prepare data - load with pandas.
    print("reading dataframe")
    df = pd.read_json(conf.events_file).set_index(conf.id_col)

    # filter season with wanted matches (by match id in config file)
    print("filtering wanted games")
    df = df.loc[df[conf.match_col].isin(conf.matches_include)]

    # read team id, add team name column
    print("adding team_name columns")
    tn=pd.read_json(conf.teams_file)
    df=df.join(tn[[conf.teamfile_name,conf.teamfile_id]].rename(
                    columns={conf.teamfile_id: conf.eventsfile_teamid,
                            conf.teamfile_name: conf.eventsfile_team_name},
                    inplace=False).set_index(conf.eventsfile_teamid),
                    on=conf.eventsfile_teamid)

    # read player id, add player_name column
    print("adding player_name columns")
    pn=pd.read_json(conf.players_file, encoding='unicode_escape')
    df= df.join(pn[[conf.playerfile_name, conf.playerfile_id]].rename(
            columns={conf.playerfile_id: conf.eventsfile_pid,
                    conf.playerfile_name: conf.eventsfile_pname},
            inplace=False).set_index(conf.eventsfile_pid),
            on=conf.eventsfile_pid)

    # fill / delete unknown players
    if conf.drop_unknown_player:
        df=df.dropna()
    else:
        df[[conf.eventsfile_pname]] = df[[conf.eventsfile_pname]].fillna(conf.unknown_pname)

    # read position (coordinates) and convert to frame
    print("adding zone columns")
    df = step.add_zone_col(df, conf.position_col, conf.zone_col, conf.zones, conf.split_x_to, conf.split_y_to)

    # convert tags from dict to list
    print("adjusting tags")
    df[conf.tags_col]=df[conf.tags_col].apply(
            lambda x: [d[conf.id_col] for d in x] )

    #fix time
    print("adjusting time")
    df=step.half_to_90min(df,halfs_col=conf.match_peroid_col, 
                          seconds_col=conf.event_sec)

    try:
        df.to_json(conf.prepare_file, orient='index',force_ascii=False)
        print("prepare file ready")
    except:
        print("cant write prepare file")
else: 
    print("reloading last data_set")
    df=pd.read_json(conf.prepare_file,encoding="unicode_escape", orient='index').set_index(conf.id_col)

# consider - event second, madftch half and last game finish time. calculate event absolute time and relative time
print("assigning case id for good moves")
df=step.get_2d_cases(df, conf.case_id_col , conf.eventsfile_team_name,
                     conf.eventsfile_teamid, conf.tags_col, conf.events_col,
                     conf.zone_col)
# save file
if conf.remove_loops:
    print("remove loops")
    df=step.remove_loops(df, conf.eventsfile_pname ,conf.case_id_col)

# open file
# set case ID by - team name, tags, event name.
# save file

# assign case id (use deticated function)
# filter only wanted cases
# create xes file?

# drop unused columns for speed?

# open file
# filter High value cases
# filter short moves (optional)
# save file

# open file
# add trace start and end states (optional)
# save file
print(df[[conf.case_id_col,conf.eventsfile_pname,conf.zone_col]])

print("writing file to csv")
df.to_csv("./data_set/all_games_no_loops.csv",float_format="%.6f")


''' 
in step 2, at any point, we can save the result to a file
and then begin from there instead
of creating again from zero
'''
# 3.analyze data with pm4py

# steps:
# open filtered json as dataframe?
print("done. working time: ",time.process_time() - start_time)