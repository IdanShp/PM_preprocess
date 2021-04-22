




# file names
data_file = 'events_Spain.json'
players_file = 'players.json'
teams_file = 'teams.json'
matches_file = 'matches_Spain.json'

# matches filter
matches_include = [2565889, 2565647, 2565777, 2565907, 2565653, 2565754, 2565781, 2565658, 2565917, 2565791, 2565922,
                  2565672, 2565807, 2565681, 2565554, 2565559, 2565817, 2565692, 2565820, 2565830, 2565704, 2565577,
                  2565580, 2565711, 2565845, 2565718, 2565592, 2565856, 2565858, 2565603, 2565737, 2565740, 2565615,
                  2565874, 2565626, 2565884, 2565629, 2565759]
matches_exclude = []


matches_to_run = matches_id

# columns rename 
col_dic = {
    "tags" : "info"
    
}

#zone mapping 
split_x_to = [33, 34, 33]
split_y_to = [25, 25, 25, 25]

#start\end nodes
with_start_end = False
