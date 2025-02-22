import tkinter as tk

def MainHelpWindow(root):
    """Opens a help window that dynamically displays keybinds."""
    help_window = tk.Toplevel(root)
    help_window.title("Help")

    # Create a dynamic help message from keybindings
    help_message = "Activity Checker:\n"
    help_message += "Can be used in order to check the activity of users in a subreddit \n"
    help_message += "Comment Reader:\n"
    help_message += "Can be used in order to quickly view the contributions of a person to a particular conversation \n"
    help_message += "Vote Analyser:\n"
    help_message += "Parses through voting records using the list of MPs and former MPs in order to quickly compile the results \n"
    help_message += "PlayerUpdater:\n"
    help_message += "Populates player.txt based on the current set of players \n"

    tk.Label(help_window, text=help_message, justify=tk.LEFT, padx=10, pady=10).pack()

def CommentReaderHelpWindow(root,keybindings):
    """Opens a help window that dynamically displays keybinds."""
    help_window = tk.Toplevel(root)
    help_window.title("Help")

    # Create a dynamic help message from keybindings
    help_message = "Keybindings:\n"
    help_message += "\n".join(f"- {key}: {action}" for action, key in keybindings.items())

    tk.Label(help_window, text=help_message, justify=tk.LEFT, padx=10, pady=10).pack()

def ActivityCheckHelpWindow(root):
    """Opens a help window that dynamically displays keybinds."""
    help_window = tk.Toplevel(root)
    help_window.title("Help")

    # Create a dynamic help message from keybindings
    help_message = "PlaceHolder AC:\n"

    tk.Label(help_window, text=help_message, justify=tk.LEFT, padx=10, pady=10).pack()

def VoteAnalyzerHelpWindow(root):
    """Opens a help window that dynamically displays keybinds."""
    help_window = tk.Toplevel(root)
    help_window.title("Help")

    # Create a dynamic help message from keybindings
    help_message = "PlaceHolder VA:\n"

    tk.Label(help_window, text=help_message, justify=tk.LEFT, padx=10, pady=10).pack()