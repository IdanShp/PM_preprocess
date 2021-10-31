import os
import pathlib
import tkinter as tk
import traceback
from tkinter import *
from tkinter import messagebox, filedialog, ttk

import unidecode

import configurations
import json

files_location = str(pathlib.Path(__file__).parent.absolute()) + "/"


def parse_all_teams():
    teams_file_path = configurations.resources_dir + 'teams.json'
    with open(teams_file_path, encoding='utf-8') as teams_file:
        data = json.load(teams_file)
        teams_full_dict = {}
        teams_comp_dict = {}
        for team_data in data:
            team_name = team_data.get('name')  # TODO: fix decode problem

            team_id = team_data.get('wyId')
            team_type = team_data.get('type')
            team_area = team_data.get('area')
            team_country = team_area.get('name')
            if team_type != 'club':
                # print("%s is not a club! is a %s" % (team_name, team_type))
                team_country = 'National'
            if team_country not in list(teams_full_dict.keys()):
                teams_full_dict[team_country] = []
                teams_comp_dict[team_country] = []
            teams_full_dict[team_country].append({'team_id': team_id, 'team_name': team_name})
            teams_comp_dict[team_country].append(team_name)
    return teams_full_dict, teams_comp_dict


def get_teams_by_league(league):
    # if league == "Spain":
    #     return ['Barcelona', 'Real']
    # if league == "Germany":
    #     return ['Bayern', 'Dortmund']
    league_teams = all_teams_names.get(league)
    return league_teams


all_teams_full_data, all_teams_names = parse_all_teams()


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
        self.master.geometry('230x250')
        self.master.resizable(width=False, height=False)
        Tk.report_callback_exception = self.show_error
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
        self.firstFrame = LabelFrame(self.master, text=" 1. Select Team: ")
        self.firstFrame.pack()
        self.insideFirstUP = Frame(self.firstFrame)
        self.insideFirstMiddle = Frame(self.firstFrame)
        self.insideFirstDown = Frame(self.firstFrame)
        self.insideFirstUP.pack()
        self.insideFirstMiddle.pack()
        self.insideFirstDown.pack()

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
                seasons_dictionary[season] = get_teams_by_league(league)
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

        # myscroll = Scrollbar(self.insideFirstDown)
        # myscroll.pack(side=RIGHT, fill=Y)
        #
        # self.mylist = Listbox(self.insideFirstDown, yscrollcommand=myscroll.set, selectbackground='Red')
        # for line in range(1, 10):
        #     self.mylist.insert(END, "")
        # self.mylist.pack(side=LEFT, fill=BOTH)

        # myscroll.config(command=self.mylist.yview)
        # l1select = self.mylist.bind('<<ListboxSelect>>', self.onselect)

        # ********Second frame********
        self.secondFrame = LabelFrame(self.master, text=" 2. Generate Analyze Report: ")
        self.secondFrame.pack()
        # ********create button***********
        self.create_button = Button(self.secondFrame, text="    Analyze    ", height=4, width=10,
                                    command=self.generate)
        self.create_button.pack(pady=15)

    def generate(self):
        final_selected_league = self.leagues_combo.get()
        final_selected_season = self.seasons_combo.get()
        final_selected_team = self.teams_combo.get()
        # final_selected_team = self.mylist.get(ACTIVE)
        if final_selected_league == 'Select League:' or final_selected_season == 'Select Season:' or \
                final_selected_team == 'Select Team:':
            return
        print(final_selected_league, final_selected_season, final_selected_team)

    def seas_combo_post_command(self):
        selected_league = self.leagues_combo.get()
        if selected_league == 'Select League:':
            return

        seasons_list = list(self.legues_dictionary[selected_league].keys())
        self.seasons_combo['values'] = seasons_list

    def team_combo_post_command(self):
        selected_league = self.leagues_combo.get()
        selected_season = self.seasons_combo.get()
        if selected_league == 'Select League:' or selected_season == 'Select Season:':
            return

        seasons_dict = self.legues_dictionary.get(selected_league)
        teams_list = seasons_dict.get(selected_season)
        self.teams_combo['values'] = teams_list

    def openFile(self):
        os.startfile(files_location + 'app_configurations.txt')
        return

    def openOut(self):
        filename = filedialog.askopenfilename(initialdir=files_location + 'Output/', title="Select File")
        os.startfile(filename)
        return

    def show_error(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror('Error', err[len(err) - 1])
        self.master.update()

    def onselect(self, event):
        selected_league = self.leagues_combo.get()
        selected_season = self.seasons_combo.get()
        if selected_league == 'Select League:' or selected_season == 'Select Season:':
            return

        seasons_dict = self.legues_dictionary.get(selected_league)
        teams_list = seasons_dict.get(selected_season)
        self.teams_combo['values'] = teams_list

        self.mylist.delete(0, END)  # clear listbox
        for i, team in enumerate(teams_list):
            self.mylist.insert(END, team)






def App_main():
    root = Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    App_main()
