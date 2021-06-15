# 


#
from datetime import datetime
from datetime import timedelta

resources_dir = "./resources/"
resources_arch = resources_dir+"resources.zip"

# file names
events_file = resources_dir+'events_Spain.json'
players_file = resources_dir+'players.json'
teams_file = resources_dir+'teams.json'
matches_file = resources_dir+'matches_Spain.json'

# matches filter
match_col="matchId"
matches_include = [2565889, 2565647, 2565777, 2565907, 2565653, 2565754, 2565781, 2565658, 2565917, 2565791, 2565922,
                  2565672, 2565807, 2565681, 2565554, 2565559, 2565817, 2565692, 2565820, 2565830, 2565704, 2565577,
                  2565580, 2565711, 2565845, 2565718, 2565592, 2565856, 2565858, 2565603, 2565737, 2565740, 2565615,
                  2565874, 2565626, 2565884, 2565629, 2565759]
# matches_include = [2565889, 2565647]
matches_exclude = []


#matches_to_run = matches_id

# columns rename 
col_dic = {
    "tags" : "info"
}

# prepare data
id_col = "id"

#zone mapping 
split_x_to = [33, 34, 33]
split_y_to = [25, 25, 25, 25]
zones = [['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3'], ['D1', 'D2', 'D3']]
position_col= "positions"
zone_col="zone"

#team file column names:
teamfile_id='wyId'
teamfile_name='name'

eventsfile_teamid = 'teamId'
eventsfile_team_name = 'team_name'

#players file columns name

playerfile_id='wyId'
playerfile_name='shortName'

eventsfile_pid = 'playerId'
eventsfile_pname = 'player_name'
drop_unknown_player=0
unknown_pname = "unknown"

# tags:
tags_col = "tags"

# adjust time
match_peroid_col = "matchPeriod"
event_sec = "eventSec"

# case id 
case_id_col = "caseId"

# get 2d cases:
events_col = "eventName"


#start\end nodes
with_start_end = False

#remove_loops
remove_loops = 1

#before caseid file path
prepare_file = "./data_set/prepare_file.json"
#after caseid file path
json_names= {
    "caseid_file" : "./data_set/caseid_file.json",
    "good_caseid_file" : "./data_set/good_caseid_file.json",
    "zone_caseid_file" : "./data_set/caseid_file.json",
    "zone_good_caseid_file" : "./data_set/good_caseid_file.json"
}
caseid_file = "./data_set/caseid_file.json"
good_caseid_file = "./data_set/good_caseid_file.json"
#after xes
xes_names={
    "player_xes_file" : "./xes/player_events_pm4py.xes",
    "player_good_xes_file" : "./xes/good_players_events_pm4py.xes",
    "zone_xes_file" : "./xes/zone_events_pm4py.xes",
    "zone_good_xes_file" : "./xes/good_zone_events_pm4py.xes",

}


# add date
begin_date= datetime.fromisoformat('2018-05-20 00:00:00.000')
time_between = timedelta(days=0, hours= 2, seconds=0, microseconds=0)
time_col='eventSec'
match_col = 'matchId'
date_col = 'date_time'

