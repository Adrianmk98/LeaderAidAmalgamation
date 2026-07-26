"""Shared visual theme, color constants, and tool descriptions used across every window."""
from ttkthemes import ThemedStyle

THEME_NAME = "arc"

TOOL_DESCRIPTIONS = {
    "Vote Analyzer": "Tally Aye/Nay/Abstain votes on a Reddit debate thread and see who hasn't voted.",
    "Activity Checker": "Check which MPs commented on qualifying debate threads within a date range.",
    "Comment Reader": "Browse a thread's comments by author, with unparliamentary-language highlighting.",
    "Player Updater": "Pull the current roster from the Google Sheet and refresh players.txt.",
}

# Vote highlight colors shared by VoteAnalyzer/voteanalyzerMain.py and VoteAnalyzer/sortingData.py
VOTE_TAG_COLORS = {
    "green_bg": "#dff5df",
    "red_bg": "#f7dada",
    "yellow_bg": "#fbf3d4",
    "no_vote_bg": "#e6e6e6",
    "graybox": "#e6e6e6",
}


def apply_theme(root):
    """Apply the shared ttk theme to a ThemedTk/Tk root and configure common shared styles."""
    style = ThemedStyle(root)
    style.set_theme(THEME_NAME)

    style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Subheading.TLabel", font=("Segoe UI", 10), foreground="#666666")
    style.configure("Card.TFrame", background="#ffffff", relief="groove", borderwidth=1)
    style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background="#ffffff")
    style.configure("CardBody.TLabel", font=("Segoe UI", 9), foreground="#555555", background="#ffffff")

    return style


def configure_vote_tags(text_widget):
    """Configure the shared Aye/Nay/Abstain/No-Vote highlight tags on a Text widget."""
    for tag, color in VOTE_TAG_COLORS.items():
        text_widget.tag_configure(tag, background=color)
