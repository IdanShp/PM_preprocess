# 


#
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
matches_exclude = []


#matches_to_run = matches_id

# columns rename 
col_dic = {
    "tags" : "info"
    
}

#zone mapping 
split_x_to = [33, 34, 33]
split_y_to = [25, 25, 25, 25]
zones = [['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3'], ['D1', 'D2', 'D3']]
position_col= "positions"
zone_col="zone"

#team name
teamid_col = "teamId"
team_name_col = "team_name"
name_file_path = players_file
namefile_id_col = "wyId"
namefile_name_col = "officialName"


#start\end nodes
with_start_end = False

#remove_loops
remove_loops = 1