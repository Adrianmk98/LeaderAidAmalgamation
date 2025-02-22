import tkinter as tk
from activityChecker import activitycheckMain
from VoteAnalyzer import voteanalyzerMain
from commentReader import commentreaderMain
from tkinter import PhotoImage

from dropDown.helpWindow import MainHelpWindow

'''

 Program Purpose: Front end of the application. Allows the user to navigate to the option they wish to use.
 
 '''

# Function to run the main function of each script
def open_activitycheck():
    activitycheckMain.main()

def open_voteanalyzer():
    voteanalyzerMain.main()

def open_commentreader():
    commentreaderMain.main()

def open_playerupdater():
    import playerUpdater
    playerUpdater.playerUpdater()

# Create the main window
root = tk.Tk()
root.title("Dashboard")
root.geometry("300x250")
logo = PhotoImage(file="logos/logored.png")
root.iconphoto(False, logo)
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
drop_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=drop_menu)
drop_menu.add_command(label="Help", command=lambda: MainHelpWindow(root))

btn_activitycheck = tk.Button(root, text="Open Activity Check", command=open_activitycheck)
btn_activitycheck.pack(pady=10)

btn_voteanalyzer = tk.Button(root, text="Open Vote Analyzer", command=open_voteanalyzer)
btn_voteanalyzer.pack(pady=10)

btn_commentreader = tk.Button(root, text="Open Comment Reader", command=open_commentreader)
btn_commentreader.pack(pady=10)

btn_playerupdater = tk.Button(root, text="Open Player Updater", command=open_playerupdater)
btn_playerupdater.pack(pady=10)

root.mainloop()
