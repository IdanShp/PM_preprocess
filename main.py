import os
import sys
import pandas as pd


#TODO give an option to create everything again

# 0.load configuration
import configurations as conf  
# source steps file. (import steps as ...)
import steps as step


# 1.prepare files
    # unzip (if necessary)
already_unzipped=1
for f in [conf.events_file,conf.players_file,conf.teams_file,conf.matches_file]:
    if not os.path.exists(conf.resources_dir+f):
        already_unzipped=0
        break
    
if not already_unzipped:
    print("extracting files from zip")
    import zipfile
    with zipfile.ZipFile(conf.resources_arch, 'r') as zip_ref:
        zip_ref.extractall(conf.resources_dir)



# 2.prepare data - load with pandas.
df = pd.read_json(conf.events_file)
    # filter wanted matches
df = df.loc[df[conf.match_col].isin(conf.matches_include)]
    # assign team names

    # assign player names
    # convert position to zone
df = step.add_zone_col(df,conf.position_col,conf.zone_col, conf.zones ,conf.split_x_to, conf.split_y_to)
    # convert time
    # drop unused columns
    # assign case id (use deticated function)
    # filter only wanted cases
    # create xes file?

print(df)
''' 
in step 2, at any point, we can save the result to a file
and then begin from there instead
of creating again from zero
''' 
# 3.analyze data with pm4py


    
    
