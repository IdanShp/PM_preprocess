import os
import sys
import pandas as pd
import pm4py
import unidecode
import time


# CREATE_NEW_DATASET = True
ASSIGN_CASE_ID = True
CREATE_XES = True
# PROCESS_MINING = True

# time for monitoring

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
    # df = pd.read_json(conf.events_file)

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
    # pn['firstName'] = map(lambda x: x.encode().decode("unicode_escape"), pn['firstName'].str)
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

    # add dates 
    print("adding date column")
    df= step.add_date(df,conf.time_col,conf.match_col, 
                        conf.date_col,conf.begin_date,conf.time_between)

    try:
        df.to_json(conf.prepare_file, orient='index',force_ascii=False, index=True)
        print("prepare file ready")
    except:
        print("cant write prepare file")


if 'ASSIGN_CASE_ID' in locals() or not os.path.exists(conf.caseid_file):
    # open file
    print("reloading last data_set")
    df=pd.read_json(conf.prepare_file,encoding="unicode_escape", orient='index', convert_dates=False, convert_axes=False)
    # consider - event second, madftch half and last game finish time. calculate event absolute time and relative time

    normal=df.copy()
    good_case=df.copy()


    # assaign normal cases.
    normal=step.assign_case_id(normal, conf.case_id_col, conf.eventsfile_teamid, conf.match_col, trace_team_id=676, max_distance=1)
    normal = normal.dropna()


    normal.to_csv("./csv/normal.csv")


    # set case ID by - team name, tags, event name.
    print("assigning case id for good moves")
    good_case=step.get_2d_cases(good_case, conf.case_id_col , conf.eventsfile_team_name,
                        conf.eventsfile_teamid, conf.tags_col, conf.events_col,
                        conf.zone_col)

    good_case.to_csv("./csv/good.csv")

    normal_zone =normal.copy()
    good_case_zone =good_case.copy()
    
    if conf.remove_loops:
        print("remove loops")
        normal=step.remove_loops(normal, conf.eventsfile_pid ,conf.case_id_col)
        good_case=step.remove_loops(good_case, conf.eventsfile_pid ,conf.case_id_col)

        normal_zone=step.remove_loops(normal_zone, conf.zone_col ,conf.case_id_col)
        good_case_zone=step.remove_loops(good_case_zone, conf.zone_col ,conf.case_id_col)

        # normal_case=step.remove_loops(df, conf.eventsfile_pid ,conf.case_id_col)
    print("writing file to csv (good for observing the data with excel")
    good_case.to_csv("./csv/good_noloops.csv")
    normal.to_csv("./csv/normal_no_loops.csv")

    try:

        normal.to_json(conf.json_names["caseid_file"], orient='index',force_ascii=False, index=True)
        good_case.to_json(conf.json_names["good_caseid_file"], orient='index',force_ascii=False, index=True)

        normal_zone.to_json(conf.json_names["zone_caseid_file"], orient='index',force_ascii=False, index=True)
        good_case_zone.to_json(conf.json_names["zone_good_caseid_file"], orient='index',force_ascii=False, index=True)
        print("caseid_file file ready")
    except:
        print("cant write caseid_file ")

if 'CREATE_XES' in locals() or not os.path.exists(conf.xes_file):


    print("reloading last case_id")
    normal=pd.read_json(conf.json_names["caseid_file"], orient='index', convert_dates=False, convert_axes=False)
    good=pd.read_json(conf.json_names["good_caseid_file"], orient='index', convert_dates=False, convert_axes=False)

    zone_normal=pd.read_json(conf.json_names["zone_caseid_file"], orient='index', convert_dates=False, convert_axes=False)
    zone_good=pd.read_json(conf.json_names["zone_good_caseid_file"], orient='index', convert_dates=False, convert_axes=False)

    #remove lists columns (make problems with converting to xes)
    normal=normal.drop(columns=[conf.tags_col, conf.position_col])
    good=good.drop(columns=[conf.tags_col, conf.position_col])

    zone_normal=zone_normal.drop(columns=[conf.tags_col, conf.position_col])
    zone_good=zone_good.drop(columns=[conf.tags_col, conf.position_col])

    # drop unused columns for speed and readability??

    #pm4py - create xes file
    print('building event log')
    # by player:
    normal_event_log = pm4py.format_dataframe(normal, case_id=conf.case_id_col, activity_key=conf.eventsfile_pname, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    good_event_log = pm4py.format_dataframe(good, case_id=conf.case_id_col, activity_key=conf.eventsfile_pname, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')

    #by zone
    normal_event_log_zone = pm4py.format_dataframe(zone_normal, case_id=conf.case_id_col, activity_key=conf.zone_col, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    good_event_log_zone = pm4py.format_dataframe(zone_good, case_id=conf.case_id_col, activity_key=conf.zone_col, timestamp_key=conf.date_col, timest_format='yyyy-mm-dd hh:mm:ss.SSSSSS')
    
    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(normal_event_log, conf.xes_names["player_xes_file"])
    xes_exporter.apply(good_event_log, conf.xes_names["player_good_xes_file"])

    xes_exporter.apply(normal_event_log_zone, conf.xes_names["zone_xes_file"])
    xes_exporter.apply(good_event_log_zone, conf.xes_names["zone_good_xes_file"])
    # pm4py.write_xes(event_log, conf.xes_file)

if 'PROCESS_MINING' in locals():
    # read log (default is the normal!)
    log = pm4py.read_xes(conf.xes_file)

    # filter short moves (optional)
    print("filtering short cases (less than 4?)")
    from pm4py.algo.filtering.log.cases import case_filter
    log = case_filter.filter_on_case_size(log,min_case_size = 4)
    print("left with ",len(log)," cases")
    # add trace start and end states (optional)

    ### start with PM algorithms ###
    # heuristic:
    map = pm4py.discover_heuristics_net(log,dependency_threshold=0.1,and_threshold=0.65, loop_two_threshold=0.5)
    pm4py.view_heuristics_net(map)

    # # inductive:
    # from pm4py.objects.log.importer.xes import importer as xes_importer
    # from pm4py.algo.discovery.inductive import algorithm as inductive_miner
    # from pm4py.visualization.process_tree import visualizer as pt_visualizer
    # from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    # from pm4py.visualization.dfg import visualizer as dfg_visualizer

    # from pm4py.visualization.petrinet import visualizer as pn_visualizer


    # net, initial_marking, final_marking = inductive_miner.apply(log)
    # tree = inductive_miner.apply_tree(log)
    # tree = inductive_miner.apply_dfg(net)
    # gviz_freq = dfg_visualizer.apply(frequency_dfg, variant=dfg_visualizer.Variants.FREQUENCY, activities_count=activities_freq, parameters={"format": "svg"})
    # dfg_visualizer.view(gviz_freq)

    # gviz = pt_visualizer.apply(tree)
    # pt_visualizer.view(gviz)

    # net to transition system
    # from pm4py.objects.petri_net.utils import reachability_graph

    # ts = reachability_graph.construct_reachability_graph(net, initial_marking)

    # from pm4py.visualization.transition_system import visualizer as ts_visualizer

    # gviz = ts_visualizer.apply(ts, parameters={ts_visualizer.Variants.VIEW_BASED.value.Parameters.FORMAT: "svg"})
    # ts_visualizer.view(gviz)



    # gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    # pn_visualizer.view(gviz)


print("done. working time: ",time.process_time() - start_time)