import tkinter as tk
from tkinter import ttk

from dropDown import theme


def _themed_help_window(root, title):
    """Create a themed Toplevel help window and return it along with a content frame."""
    help_window = tk.Toplevel(root)
    help_window.title(title)
    theme.apply_theme(help_window)

    content = ttk.Frame(help_window, padding=16)
    content.pack(fill="both", expand=True)
    ttk.Label(content, text=title, style="Heading.TLabel").pack(anchor="w", pady=(0, 10))
    return help_window, content


def _section(parent, heading, body):
    ttk.Label(parent, text=heading, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
    ttk.Label(parent, text=body, justify=tk.LEFT, wraplength=420).pack(anchor="w")


def MainHelpWindow(root):
    """Opens a help window summarizing what each of the four tools does."""
    _, content = _themed_help_window(root, "CMHoC Toolkit — Help")

    for name in ("Activity Checker", "Vote Analyzer", "Comment Reader", "Player Updater"):
        _section(content, name, theme.TOOL_DESCRIPTIONS[name])


def CommentReaderHelpWindow(root, keybindings):
    """Opens a help window that dynamically displays keybinds."""
    _, content = _themed_help_window(root, "Comment Reader — Help")

    _section(
        content,
        "What it does",
        theme.TOOL_DESCRIPTIONS["Comment Reader"] + " Usernames mentioned in a comment are "
        "highlighted in blue, and words flagged in the unparliamentary-language list are "
        "highlighted in red. Comments can be marked as read, which highlights them in green.",
    )

    ttk.Label(content, text="Keybindings", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
    for action, key in keybindings.items():
        ttk.Label(content, text=f"- {key}: {action}").pack(anchor="w")


def ActivityCheckHelpWindow(root):
    """Opens a help window describing the Activity Checker tool."""
    _, content = _themed_help_window(root, "Activity Checker — Help")

    _section(
        content,
        "What it does",
        theme.TOOL_DESCRIPTIONS["Activity Checker"] + " Only posts flaired as Question Period, "
        "2nd Reading, Committee of the Whole, Motion Debate, Report Stage, 3rd Reading, "
        "Take-Note Debate, or Motion Amendments in r/cmhoc are counted as qualifying debates.",
    )
    _section(
        content,
        "How to use it",
        "Pick a start and end date, then click \"Check Comments\". Every currently incumbent MP "
        "is listed: green means they commented on a qualifying thread in that window, red means "
        "no comments were found. Select a name to see links to each comment that counted.",
    )


def VoteAnalyzerHelpWindow(root):
    """Opens a help window describing the Vote Analyzer tool."""
    _, content = _themed_help_window(root, "Vote Analyzer — Help")

    _section(
        content,
        "What it does",
        theme.TOOL_DESCRIPTIONS["Vote Analyzer"] + " It scans every comment on a Reddit thread "
        "and matches each MP's most recent comment against Aye/Nay/Abstain keywords (with some "
        "tolerance for typos and French equivalents: aye/oui/yea/pour, nay/non/contre, "
        "abstain/abstention).",
    )
    _section(
        content,
        "How to use it",
        "Paste a thread link (or use \"Open Recent Posts\" to browse recent threads in "
        "r/cmhocvote) and click \"Analyze Votes\". Use the sort buttons to reorganize the "
        "breakdown by vote type, party, or government position.",
    )


def PlayerUpdaterHelpWindow(root):
    """Opens a help window describing the Player Updater tool."""
    _, content = _themed_help_window(root, "Player Updater — Help")

    _section(
        content,
        "What it does",
        theme.TOOL_DESCRIPTIONS["Player Updater"] + " It reads the \"Voting Records\" worksheet "
        "of the configured Google Sheet and overwrites includes/players.txt with the current "
        "roster. Any member removed from the sheet since the last sync is appended to "
        "includes/oldplayer.txt.",
    )
    _section(
        content,
        "How to use it",
        "Click \"Refresh Roster\" and watch the log for progress. This overwrites "
        "includes/players.txt, which every other tool reads from — only run it when you intend "
        "to update the roster used across the whole toolkit.",
    )
