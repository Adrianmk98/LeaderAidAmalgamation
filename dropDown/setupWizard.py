"""First-run setup wizard: collects Reddit API credentials and initializes/imports the
player roster database, so a new install doesn't have to hand-edit ini files or hit a raw
exception before the dashboard becomes usable."""
import configparser
import os
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk

import praw

from config import setupCheck
from includes import playerDB
from dropDown import theme

DEFAULT_USER_AGENT = "script:cmhocApp:v1.0 (by /u/your_username)"


def _write_reddit_config(client_id, client_secret, user_agent):
    config = configparser.ConfigParser()
    config['reddit'] = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent,
    }
    with open('config/config.ini', 'w') as f:
        config.write(f)


def _players_txt_path():
    config = configparser.ConfigParser()
    config.read('config/locationOfTxt.ini')
    return config['player']['playerFile']


class _SetupWizard:
    def __init__(self):
        self.rootx = ThemedTk(theme=theme.THEME_NAME)
        self.rootx.withdraw()
        self.root = tk.Toplevel(self.rootx)
        self.root.title("CMHoC Toolkit - First-Time Setup")
        self.root.geometry("560x480")
        self.root.minsize(520, 440)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        theme.apply_theme(self.root)

        ttk.Label(self.root, text="Welcome to the CMHoC Toolkit", style="Heading.TLabel").pack(
            anchor="w", padx=16, pady=(14, 0)
        )
        ttk.Label(
            self.root,
            text="Let's get the app configured before you start moderating.",
            style="Subheading.TLabel",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self._build_reddit_section()
        self._build_roster_section()

        footer = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        footer.pack(fill="x", side="bottom")
        self.finish_button = ttk.Button(footer, text="Finish", command=self._on_close, state=tk.DISABLED)
        self.finish_button.pack(side="right")

        self._refresh_status()

    def _build_reddit_section(self):
        frame = ttk.LabelFrame(self.root, text="Step 1 - Reddit API Credentials", padding=10)
        frame.pack(fill="x", padx=16, pady=(0, 8))

        ttk.Label(
            frame,
            text="Create a 'script' app at reddit.com/prefs/apps, then enter its details below.",
            style="CardBody.TLabel",
            wraplength=500,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(frame, text="Client ID:").grid(row=1, column=0, sticky="w", pady=2)
        self.client_id_entry = ttk.Entry(frame, width=40)
        self.client_id_entry.grid(row=1, column=1, sticky="we", pady=2)

        ttk.Label(frame, text="Client Secret:").grid(row=2, column=0, sticky="w", pady=2)
        self.client_secret_entry = ttk.Entry(frame, width=40, show="*")
        self.client_secret_entry.grid(row=2, column=1, sticky="we", pady=2)

        ttk.Label(frame, text="User Agent:").grid(row=3, column=0, sticky="w", pady=2)
        self.user_agent_entry = ttk.Entry(frame, width=40)
        self.user_agent_entry.insert(0, DEFAULT_USER_AGENT)
        self.user_agent_entry.grid(row=3, column=1, sticky="we", pady=2)

        frame.columnconfigure(1, weight=1)

        self.reddit_status_label = ttk.Label(frame, text="", style="CardBody.TLabel")
        self.reddit_status_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Button(frame, text="Test & Save", command=self._test_and_save_reddit).grid(
            row=5, column=1, sticky="e", pady=(6, 0)
        )

    def _build_roster_section(self):
        self.roster_frame = ttk.LabelFrame(self.root, text="Step 2 - Player Roster", padding=10)
        self.roster_frame.pack(fill="x", padx=16, pady=(0, 8))
        self.roster_status_label = ttk.Label(self.roster_frame, text="", style="CardBody.TLabel", wraplength=500)
        self.roster_status_label.pack(anchor="w")
        self.roster_action_button = ttk.Button(self.roster_frame, text="")
        self.roster_action_button.pack(anchor="w", pady=(6, 0))

    def _refresh_status(self):
        if setupCheck.has_valid_reddit_config():
            self.reddit_status_label.config(text="Reddit credentials look good.")
            self.finish_button.config(state=tk.NORMAL)
        else:
            self.finish_button.config(state=tk.DISABLED)

        self._refresh_roster_section()

    def _refresh_roster_section(self):
        has_db = setupCheck.has_player_db()
        txt_path = _players_txt_path()
        has_txt = os.path.exists(txt_path)

        if has_db:
            conn = playerDB.get_connection()
            try:
                count = conn.execute("SELECT COUNT(*) FROM players WHERE is_vacant = 0").fetchone()[0]
            finally:
                conn.close()
            self.roster_status_label.config(text=f"Roster already loaded ({count} players).")
            self.roster_action_button.config(text="Re-import from players.txt", command=self._import_roster)
        elif has_txt:
            self.roster_status_label.config(
                text=f"Found an existing {txt_path} - import it into the roster database now?"
            )
            self.roster_action_button.config(text="Import", command=self._import_roster)
        else:
            self.roster_status_label.config(
                text="No roster found yet. You can start with an empty roster and populate it later "
                     "using the Player Updater tool, or place a players.txt file in includes/ and "
                     "re-open this wizard."
            )
            self.roster_action_button.config(text="Continue with empty roster", command=self._create_empty_roster)

    def _test_and_save_reddit(self):
        client_id = self.client_id_entry.get().strip()
        client_secret = self.client_secret_entry.get().strip()
        user_agent = self.user_agent_entry.get().strip()

        if not (client_id and client_secret and user_agent):
            self.reddit_status_label.config(text="All three fields are required.")
            return

        try:
            praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        except Exception as e:
            self.reddit_status_label.config(text=f"Couldn't build a Reddit client: {e}")
            return

        _write_reddit_config(client_id, client_secret, user_agent)
        self._refresh_status()

    def _import_roster(self):
        try:
            rows_imported, vacant_count = playerDB.import_from_txt()
        except Exception as e:
            messagebox.showerror("Player Roster", f"Import failed:\n{e}")
            return
        self.roster_status_label.config(
            text=f"Imported {rows_imported} players ({vacant_count} vacant seats)."
        )
        self._refresh_status()

    def _create_empty_roster(self):
        playerDB.ensure_schema()
        self._refresh_status()

    def _on_close(self):
        self.rootx.destroy()

    def run(self):
        self.rootx.mainloop()


def run_wizard():
    _SetupWizard().run()


if __name__ == "__main__":
    run_wizard()
