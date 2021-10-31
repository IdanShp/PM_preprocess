import os
import pathlib
import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog, ttk
import configurations
import json

files_location = str(pathlib.Path(__file__).parent.absolute()) + "/"

def parse_all_teams():
    teams_file_path = configurations.resources_dir + 'teams.json'
    with open(teams_file_path) as teams_file:
        data = json.load(teams_file)
        teams_dict = {}
        for team_data in data:
            team_name = team_data.get('name')
            team_id = team_data.get('wyId')
            team_type = team_data.get('type')
            team_area = team_data.get('area')
            team_country = team_area.get('name')
            if team_type != 'club':
                print("%s is not a club!" % team_name)

        teams_dict[team_country] = ""



def get_teams_by_league_season(league, season):

    if league == "Spain":
        return ['Barcelona', 'Real']
    if league == "Germany":
        return ['Bayern', 'Dortmund']
    return
    pass


class MainWindow():
    def __init__(self, master):
        # *******configurations********
        with open(files_location + "app_configurations.txt") as config_file:
            self.configurations = config_file.read().splitlines()
        # **********Create*************
        self.master = master
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)
        self.master.wm_iconbitmap('pics/ball_icon.ico')
        self.master.title('Demo')
        self.master.resizable(width=False, height=False)
        # Tk.report_callback_exception = self.show_error  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.newWindow = None
        self.app = None
        self.status_msg = StringVar()
        self.status_msg.set("Ready")
        # ***********Menu Bar************
        file_menu = Menu(self.menu)
        file_menu.config(tearoff=0)
        open_menu = Menu(file_menu)
        open_menu.config(tearoff=0)
        edit_menu = Menu(self.menu)
        edit_menu.config(tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        self.menu.add_cascade(label="Edit", menu=edit_menu)
        file_menu.add_cascade(label="Open", menu=open_menu)
        open_menu.add_command(label="Open Configurations", command=self.openFile)
        open_menu.add_command(label="Open Output Folder", command=self.openOut)

        # ********first frame********
        self.firstFrame = LabelFrame(self.master, text=" 1. Enter Details: ")
        self.firstFrame.grid(row=0, sticky=E + W, padx=5)
        self.insideFirstUP = Frame(self.firstFrame)
        self.insideFirstMiddle = Frame(self.firstFrame)
        self.insideFirstDown = Frame(self.firstFrame)
        self.insideFirstUP.grid(row=0, sticky=E + W)
        self.insideFirstMiddle.grid(row=1, sticky=W)
        self.insideFirstDown.grid(row=2, sticky=E + W)

        resources_dir = configurations.resources_dir

        leagues_list = os.listdir(resources_dir)
        leagues_list = [name for name in leagues_list if ".json" not in name]  # remove 'players.json', 'teams.json'

        # leagues_list = ["Option1", "Option2", "Option3", "Option4", "Option5"]
        self.legues_dictionary = {}
        for league in leagues_list:
            seasons_dictionary = {}
            seasons_list = os.listdir(resources_dir + '/' + league)
            seasons_list = [season.replace('_', '/') for season in seasons_list]

            for season in seasons_list:
                seasons_dictionary[season] = get_teams_by_league_season(league, season)
            self.legues_dictionary[league] = seasons_dictionary

            # teams_dictionary[league] = seasons_dictionary[]

        self.leagues_combo = ttk.Combobox(self.insideFirstUP, values=list(self.legues_dictionary.keys()))
        self.leagues_combo.set("Select League:")
        self.leagues_combo.pack(padx=5, pady=5)

        self.seasons_combo = ttk.Combobox(self.insideFirstMiddle, values=[], postcommand=self.seas_combo_post_command)
        self.seasons_combo.set("Select Season:")
        self.seasons_combo.pack(padx=5, pady=5)

        self.teams_combo = ttk.Combobox(self.insideFirstDown, values=[], postcommand=self.team_combo_post_command)
        self.teams_combo.set("Select Team:")
        self.teams_combo.pack(padx=5, pady=5)

        selected_league = self.leagues_combo.get()
        print(selected_league)
        # seasons_combo['values'] = list(legues_dictionary[selected_league].keys())
        # selected_season = seasons_combo.get()

        # selected_league = leagues_combo.get()
        # print(legues_dictionary[selected_league])

    def seas_combo_post_command(self):
        selected_league = self.leagues_combo.get()
        seasons_list = list(self.legues_dictionary[selected_league].keys())
        self.seasons_combo['values'] = seasons_list

    def team_combo_post_command(self):
        selected_league = self.leagues_combo.get()
        selected_season = self.seasons_combo.get()
        seasons_dict = self.legues_dictionary.get(selected_league)
        teams_list = seasons_dict.get(selected_season)
        self.teams_combo['values'] = teams_list

    def openFile(self):
        os.startfile(files_location + 'app_configurations.txt')
        return

    def openOut(self):
        filename = filedialog.askopenfilename(initialdir=files_location + 'output/', title="Select File")
        os.startfile(filename)
        return


def App_main():
    root = Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    App_main()
