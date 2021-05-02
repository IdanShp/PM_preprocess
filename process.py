import pandas
import pm4py
from pm4py.visualization.sna import visualizer as sna_visualizer
from pm4py.algo.organizational_mining.sna import algorithm as sna

file_path = 'C:/Users/Idan Shpirer/Dropbox/Project Idan Snir PM/DataSets/processed_data/data_for_discovery_2_games.csv'

event_log = pandas.read_csv(file_path, sep=',')
event_log = pm4py.format_dataframe(event_log, case_id='caseId', activity_key='Player Name',
                                   timestamp_key='relEventTime', timest_format='mmm:ss.SSSS',)

pm4py.write_xes(event_log, 'C:/Users/Idan Shpirer/Dropbox/Project Idan Snir PM/DataSets/processed_data/data_for_replay_2_games.xes')

log = pm4py.read_xes("C:/Users/Idan Shpirer/Dropbox/Project Idan Snir PM/DataSets/processed_data/data_for_replay_2_games.xes")

hw_values = sna.apply(log, variant=sna.Variants.HANDOVER_LOG)
gviz_hw_py = sna_visualizer.apply(hw_values, variant=sna_visualizer.Variants.PYVIS)
sna_visualizer.view(gviz_hw_py, variant=sna_visualizer.Variants.PYVIS)
