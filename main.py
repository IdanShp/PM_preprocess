import os
import sys
import pandas as pd

# time for monitoring
import time

# TODO give an option to create everything again

# 0.load configuration
import configurations as conf
# source steps file. (import steps as ...)
import steps as step

start_time = time.process_time()

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
df = pd.read_json(conf.events_file).set_index('id')

# filter season with wanted matches (by match id in config file)
df = df.loc[df[conf.match_col].isin(conf.matches_include)]

# read team id, add team name column
tn=pd.read_json(conf.teams_file)
df=df.join(tn[['name','wyId']].rename(columns={'wyId':'teamId','name':'team_name'}, inplace=False).set_index('teamId') , on='teamId')

# read player id, add player name column
pn=pd.read_json(conf.players_file)
df= df.join(pn[['shortName','wyId']].rename(columns={'wyId':'playerId','shortName':'Player_name'}, inplace=False).set_index('playerId') , on='playerId')

# read position (coordinates) and convert to frame
df = step.add_zone_col(df, conf.position_col, conf.zone_col, conf.zones, conf.split_x_to, conf.split_y_to)

# convert tags from dict to list
df['tags']=df['tags'].apply(lambda x: [d['id'] for d in x] )

# consider - event second, madftch half and last game finish time. calculate event absolute time and relative time
df=step.get_2d_cases(df)
# save file
if conf.remove_loops:
    df=step.remove_loops(df, "Player_name","caseId")

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
print(df[["caseId","Player_name","zone"]])

df.to_csv("./data_set/all_games_no_loops.csv", index=False ,float_format="%.6f")


''' 
in step 2, at any point, we can save the result to a file
and then begin from there instead
of creating again from zero
'''
# 3.analyze data with pm4py

# steps:
# open filtered json as dataframe?
print(time.process_time() - start_time)