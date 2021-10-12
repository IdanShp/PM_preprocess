import os
import sys
import pandas as pd
import pm4py
import unidecode
import time


CREATE_NEW_DATASET = True
ASSIGN_CASE_ID = True
CREATE_XES = True
# PROCESS_MINING = True

# time for monitoring


# 1.load configuration
import configurations as conf
import steps as step


# monitor runing time
start_time = time.process_time()

if 'CREATE_NEW_DATASET' in locals() or not os.path.exists(conf.prepare_file):
    print("creating new data_set")

    # 1.prepare files
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
    # df = pd.read_json(conf.events_file)

    # filter season with wanted matches (by match id in config file)
    print("filtering wanted games")
    df = df.loc[df[conf.match_col].isin(conf.matches_include)]

    # add team_name column by team id
    print("adding team_name columns")
    tn=pd.read_json(conf.teams_file)
    df=df.join(tn[[conf.teamfile_name,conf.teamfile_id]].rename(
                    columns={conf.teamfile_id: conf.eventsfile_teamid,
                            conf.teamfile_name: conf.eventsfile_team_name},
                    inplace=False).set_index(conf.eventsfile_teamid),
                    on=conf.eventsfile_teamid)

    # add player_name column by player id
    print("adding player_name columns")
    pn=pd.read_json(conf.players_file, encoding='unicode_escape')
    pn['shortName'] = list(map(lambda x: unidecode.unidecode(x), pn['shortName']))

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

    # read position (coordinates) and convert to zone
    print("adding zone columns")
    df = step.add_zone_col(df, conf.position_col, conf.zone_col, conf.zones, conf.split_x_to, conf.split_y_to)

    # convert tags from dict type to a list
    print("adjusting tags")
    df[conf.tags_col]=df[conf.tags_col].apply(
            lambda x: [d[conf.id_col] for d in x] )

    # fix time
    print("adjusting time")
    df=step.half_to_90min(df,halfs_col=conf.match_peroid_col, 
                          seconds_col=conf.event_sec)

    # add dates (prevet game from overlapping in time)
    print("adding date column")
    df= step.add_date(df,conf.time_col,conf.match_col, 
                        conf.date_col,conf.begin_date,conf.time_between)

    try:
        df.to_json(conf.prepare_file, orient='index',**conf.to_json_args)
        print("prepare file ready")
    except:
        print("cant write prepare file")


if 'ASSIGN_CASE_ID' in locals() or not os.path.exists(conf.prepare_file):
    # open file
    print("reloading last data_set")
    df=pd.read_json(conf.prepare_file,encoding="unicode_escape", orient='index', **conf.read_json_args)

    # assaign case id. (676 team id is barcelona)
    # TODO: remove magic number
    normal=step.assign_case_id(df, conf.case_id_col, conf.eventsfile_teamid, conf.match_col, trace_team_id=676, max_distance=1)
    
    print("save all case id, loops not removed yet")
    normal.to_csv("./csv/normal_with_loops.csv")

    #make dataframe for zones
    normal_zone =normal.copy()

    if conf.remove_loops:
        print("remove players loops")
        normal=step.remove_loops(normal, conf.eventsfile_pid ,conf.case_id_col)
        print("remove zone loops")
        normal_zone=step.remove_loops(normal_zone, conf.zone_col ,conf.case_id_col)

    # filter good and bad cases
    print("filter good cases and bad cases")
    good_case = step.get_2d_cases_v2(normal, conf.case_id_col,conf.events_col,conf.zone_col)
    good_case_zone = step.get_2d_cases_v2(normal_zone, conf.case_id_col,conf.events_col,conf.zone_col)

    bad_players=step.substruct_log_from_log(normal,good_case,conf.case_id_col)
    bad_zones=step.substruct_log_from_log(normal_zone,good_case_zone,conf.case_id_col)


    #write csv files for observation 
    while True:
        try:
            print("writing file to csv (good for observing the data with excel")
            good_case.to_csv(conf.csv_names["players"], **conf.to_csv_args)
            normal.to_csv(conf.csv_names["players_good"], **conf.to_csv_args)
            bad_players.to_csv(conf.csv_names["players_bad"], **conf.to_csv_args)
            good_case_zone.to_csv(conf.csv_names["zone"], **conf.to_csv_args)
            normal_zone.to_csv(conf.csv_names["zone_good"], **conf.to_csv_args)
            bad_zones.to_csv(conf.csv_names["zone_bad"], **conf.to_csv_args)
            break

        except PermissionError:
            print("one of the files is open. close it and pres enter")
            input()


    #save json for next stage
    try:
        normal.to_json(conf.json_names["caseid_file"], orient='index',**conf.to_json_args)
        good_case.to_json(conf.json_names["good_caseid_file"], orient='index',**conf.to_json_args)
        bad_players.to_json(conf.json_names["bad_caseid_file"], orient='index',**conf.to_json_args)

        normal_zone.to_json(conf.json_names["zone_caseid_file"], orient='index',**conf.to_json_args)
        good_case_zone.to_json(conf.json_names["zone_good_caseid_file"], orient='index',**conf.to_json_args)
        bad_zones.to_json(conf.json_names["zone_bad_caseid_file"], orient='index',**conf.to_json_args)
        print("caseid_file file ready")
    except:
        print("cant write caseid_file ")

if 'CREATE_XES' in locals():

    print("reloading last case_id")
    normal=pd.read_json(conf.json_names["caseid_file"], orient='index', **conf.read_json_args)
    good=pd.read_json(conf.json_names["good_caseid_file"], orient='index', **conf.read_json_args)
    bad=pd.read_json(conf.json_names["bad_caseid_file"], orient='index', **conf.read_json_args)

    zone_normal=pd.read_json(conf.json_names["zone_caseid_file"], orient='index', **conf.read_json_args)
    zone_good=pd.read_json(conf.json_names["zone_good_caseid_file"], orient='index', **conf.read_json_args)
    zone_bad=pd.read_json(conf.json_names["zone_bad_caseid_file"], orient='index', **conf.read_json_args)

    #remove lists columns (make problems when converting to xes)
    normal=normal.drop(columns=[conf.tags_col, conf.position_col])
    good=good.drop(columns=[conf.tags_col, conf.position_col])
    bad=bad.drop(columns=[conf.tags_col, conf.position_col])

    zone_normal=zone_normal.drop(columns=[conf.tags_col, conf.position_col])
    zone_good=zone_good.drop(columns=[conf.tags_col, conf.position_col])
    zone_bad=zone_bad.drop(columns=[conf.tags_col, conf.position_col])

    # drop unused columns for speed and readability??

    #pm4py - create xes file
    print('building event log')
    # by player:
    normal_event_log = pm4py.format_dataframe(normal, case_id=conf.case_id_col, activity_key=conf.eventsfile_pname, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    good_event_log = pm4py.format_dataframe(good, case_id=conf.case_id_col, activity_key=conf.eventsfile_pname, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    bad_event_log = pm4py.format_dataframe(bad, case_id=conf.case_id_col, activity_key=conf.eventsfile_pname, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')

    #by zone
    normal_event_log_zone = pm4py.format_dataframe(zone_normal, case_id=conf.case_id_col, activity_key=conf.zone_col, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    good_event_log_zone = pm4py.format_dataframe(zone_good, case_id=conf.case_id_col, activity_key=conf.zone_col, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    bad_event_log_zone = pm4py.format_dataframe(zone_bad, case_id=conf.case_id_col, activity_key=conf.zone_col, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    
    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(normal_event_log, conf.xes_names["player_xes_file"])
    xes_exporter.apply(good_event_log, conf.xes_names["player_good_xes_file"])
    xes_exporter.apply(bad_event_log, conf.xes_names["player_bad_xes_file"])

    xes_exporter.apply(normal_event_log_zone, conf.xes_names["zone_xes_file"])
    xes_exporter.apply(good_event_log_zone, conf.xes_names["zone_good_xes_file"])
    xes_exporter.apply(bad_event_log_zone, conf.xes_names["zone_bad_xes_file"])


print("done. working time: ",time.process_time() - start_time)