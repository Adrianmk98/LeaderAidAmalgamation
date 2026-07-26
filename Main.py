import sys
import tkinter as tk
from tkinter import ttk, PhotoImage, messagebox
from ttkthemes import ThemedTk

from activityChecker import activitycheckMain
from VoteAnalyzer import voteanalyzerMain
from commentReader import commentreaderMain
from ElectionSimulator import electionsimulatorMain

from config import setupCheck
from dropDown.helpWindow import MainHelpWindow
from dropDown.setupWizard import run_wizard
from dropDown import theme

# On first run (or if config/config.ini or the player roster DB is missing/invalid), walk the
# user through setup instead of opening a dashboard full of tools that will just fail later.
if not (setupCheck.has_valid_reddit_config() and setupCheck.has_player_db()):
    run_wizard()
    if not (setupCheck.has_valid_reddit_config() and setupCheck.has_player_db()):
        _warn_root = tk.Tk()
        _warn_root.withdraw()
        messagebox.showwarning(
            "Setup incomplete",
            "Setup wasn't finished, so the toolkit can't start yet. Re-launch the app to try again.",
            master=_warn_root,
        )
        _warn_root.destroy()
        sys.exit(0)

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
    from playerUpdater import playerUpdaterMain
    playerUpdaterMain.main()

def open_electionsimulator():
    electionsimulatorMain.main()

# Tool cards: display name, description key, logo file, subsample factor (to shrink 256/467px logos
# down to a consistent ~50px icon), and the launcher function.
TOOLS = [
    ("Activity Checker", "logos/logoorange.png", 5, open_activitycheck),
    ("Vote Analyzer", "logos/logoblue.png", 5, open_voteanalyzer),
    ("Comment Reader", "logos/logoblue.png", 5, open_commentreader),
    ("Player Updater", "logos/logogreen.png", 9, open_playerupdater),
    ("Election Simulator", "ElectionSimulator/electionPage/imgs/CMHoC_Logo.png", 13, open_electionsimulator),
]

# Create the main window
root = ThemedTk(theme=theme.THEME_NAME)
root.title("CMHoC Toolkit")
root.geometry("560x460")
root.minsize(480, 420)

logo = PhotoImage(file="logos/logored.png", master=root)
root.iconphoto(False, logo)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
drop_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=drop_menu)
drop_menu.add_command(label="Help", command=lambda: MainHelpWindow(root))
drop_menu.add_command(label="Re-run Setup Wizard", command=run_wizard)

theme.apply_theme(root)

header_frame = ttk.Frame(root, padding=(20, 20, 20, 10))
header_frame.pack(fill="x")
ttk.Label(header_frame, text="CMHoC Toolkit", style="Heading.TLabel").pack(anchor="w")
ttk.Label(
    header_frame,
    text="Pick a tool to work with the CMHoC subreddit and member roster.",
    style="Subheading.TLabel",
).pack(anchor="w")

cards_frame = ttk.Frame(root, padding=(20, 0, 20, 20))
cards_frame.pack(fill="both", expand=True)

_card_icons = []  # keep PhotoImage references alive

for name, logo_path, subsample, open_fn in TOOLS:
    card = ttk.Frame(cards_frame, style="Card.TFrame", padding=12)
    card.pack(fill="x", pady=6)

    icon = PhotoImage(file=logo_path, master=root).subsample(subsample, subsample)
    _card_icons.append(icon)
    icon_label = ttk.Label(card, image=icon, style="CardTitle.TLabel")
    icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 12))

    ttk.Label(card, text=name, style="CardTitle.TLabel").grid(row=0, column=1, sticky="w")
    ttk.Label(
        card, text=theme.TOOL_DESCRIPTIONS[name], style="CardBody.TLabel", wraplength=340
    ).grid(row=1, column=1, sticky="w")

    ttk.Button(card, text="Open", command=open_fn).grid(row=0, column=2, rowspan=2, padx=(12, 0))
    card.columnconfigure(1, weight=1)

root.mainloop()
