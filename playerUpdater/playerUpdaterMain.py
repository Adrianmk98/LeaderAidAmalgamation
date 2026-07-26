import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ttkthemes import ThemedTk

from playerUpdater.playerUpdater import playerUpdater
from dropDown.helpWindow import PlayerUpdaterHelpWindow
from dropDown import theme

'''

 Program Purpose: GUI front end for playerUpdater.playerUpdater() — pulls the current roster from
 the Google Sheet and rewrites includes/players.txt, showing progress and errors instead of running
 silently.

 '''


def _log(message):
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
    log_box.config(state=tk.DISABLED)


def _run_update():
    refresh_button.config(state=tk.DISABLED)
    log_box.config(state=tk.NORMAL)
    log_box.delete(1.0, tk.END)
    log_box.config(state=tk.DISABLED)
    try:
        playerUpdater(log=_log)
    except Exception as e:
        _log(f"Error: {e}")
        messagebox.showerror("Player Updater", f"Roster sync failed:\n{e}")
    finally:
        refresh_button.config(state=tk.NORMAL)


def run_update():
    thread = threading.Thread(target=_run_update)
    thread.start()


def main():
    global root, refresh_button, log_box

    rootx = ThemedTk(theme=theme.THEME_NAME)
    rootx.withdraw()
    root = tk.Toplevel(rootx)
    root.title("CMHoC Player Updater")
    root.geometry("640x480")
    root.minsize(520, 400)
    logo = tk.PhotoImage(file="logos/logogreen.png", master=root)
    root.iconphoto(True, logo)

    theme.apply_theme(root)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    drop_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=drop_menu)
    drop_menu.add_command(label="Help", command=lambda: PlayerUpdaterHelpWindow(root))

    ttk.Label(root, text="Player Updater", style="Heading.TLabel").pack(anchor="w", padx=16, pady=(14, 0))
    ttk.Label(
        root, text=theme.TOOL_DESCRIPTIONS["Player Updater"], style="Subheading.TLabel"
    ).pack(anchor="w", padx=16, pady=(0, 8))

    sync_frame = ttk.LabelFrame(root, text="Roster Sync", padding=10)
    sync_frame.pack(fill="x", padx=16, pady=(0, 8))

    refresh_button = ttk.Button(sync_frame, text="Refresh Roster", command=run_update)
    refresh_button.pack(anchor="w")

    log_frame = ttk.LabelFrame(root, text="Log", padding=8)
    log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    log_box = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
    log_box.pack(fill="both", expand=True)

    rootx.mainloop()


if __name__ == "__main__":
    main()
