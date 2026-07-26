import configparser
import praw
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import time
import threading
import webbrowser
import tkinter as tk
import pyperclip
from ttkthemes import ThemedTk

from includes.playerDB import load_usernames_and_parties
from dropDown.helpWindow import ActivityCheckHelpWindow
from config.getRedditCreds import fetch_reddit_creds
from dropDown import theme

'''

 Program Purpose: Creates a gui which allows for input of a start date, and end date for the comment search.
 The reddit API will search all posts in the indicated subreddit with certain flairs in order to determine which players from players.txt have sufficient activity.

 '''

# List of specific flairs to check in CMHoC since any other flairs do not qualify
TARGET_FLAIRS = [
    "⚔️ Question Period",
    "2nd Reading",
    "Committee of the Whole",
    "Motion Debate",
    "Report Stage",
    "3rd Reading",
    "Take-Note Debate",
    "Motion Amendments"
]

# Global dictionaries to hold user comment details
user_comment_details = {}
user_found = {}


# Function to check comments within time period
def check_comments():
    global user_found
    subreddit = "cmhoc"
    result_textbox.delete(0, tk.END)
    details_textbox.delete(1.0, tk.END)
    status_label.config(text="Checking comments, please wait...")
    try:
        start_time = time.mktime(calendar_start.get_date().timetuple())
        end_time = time.mktime(calendar_end.get_date().timetuple())
        post_start_time = start_time - 5 * 24 * 3600 #-5 so it applies to EST
        post_end_time = end_time + 5 * 24 * 3600
        usernames_and_parties = load_usernames_and_parties()
        if not usernames_and_parties:
            status_label.config(text="No players loaded — check the player data file.")
            return
        user_found = {username: [] for username, party in usernames_and_parties}
        users_not_found = {username for username, party in usernames_and_parties}
        subreddit = reddit.subreddit(subreddit)
        for post in subreddit.new(limit=None):
            post_time = post.created_utc
            if post_start_time <= post_time <= post_end_time and post.link_flair_text in TARGET_FLAIRS:
                post.comments.replace_more(limit=None)
                for comment in post.comments.list():
                    if comment.author:
                        comment_author = comment.author.name
                        comment_time = comment.created_utc
                        if start_time <= comment_time <= end_time:
                            if comment_author in user_found:
                                users_not_found.discard(comment_author)
                                comment_time_str = datetime.utcfromtimestamp(comment_time).strftime('%Y-%m-%d %H:%M:%S')
                                comment_link = f"https://www.reddit.com{comment.permalink}"
                                post_title = post.title  # Get the post title
                                comment_detail = {
                                    "subreddit": subreddit,
                                    "time": comment_time_str,
                                    "link": comment_link,
                                    "post_title": post_title
                                }
                                user_found[comment_author].append(comment_detail)
        found_count = 0
        for username, party in usernames_and_parties:
            if user_found[username]:
                found_count += 1
                result_textbox.insert(tk.END, f"{username} ({party}) - Comments found\n")
                result_textbox.itemconfig(tk.END, {'fg': 'green'})
            else:
                result_textbox.insert(tk.END, f"{username} ({party}) - No comments\n")
                result_textbox.itemconfig(tk.END, {'fg': 'red'})
        status_label.config(
            text=f"Done — {found_count} of {len(usernames_and_parties)} MPs have qualifying comments."
        )
    except Exception as e:
        status_label.config(text=f"Error during comment checking: {e}")

# Function to run the check_comments in a separate thread
def run_check_comments():
    thread = threading.Thread(target=check_comments)
    thread.start()

# Function to display user details with clickable buttons for links
def display_user_details(event):
    selected_index = result_textbox.curselection()
    if selected_index:
        selected_entry = result_textbox.get(selected_index[0])
        selected_username = selected_entry.split(" (")[0]
        details_textbox.delete(1.0, tk.END)
        if selected_username in user_found:
            details_textbox.insert(tk.END, f"Details for {selected_username}:\n\n")
            details_textbox.insert(tk.END, "-" * 60 + "\n\n")
            for detail in user_found[selected_username]:
                post_title = detail["post_title"]
                time_line = detail["time"]
                link_url = detail["link"]

                # Display the post title, time, and URL
                details_textbox.insert(tk.END, f"Post Title: {post_title}\n")
                details_textbox.insert(tk.END, f"Time: {time_line}\n")
                details_textbox.insert(tk.END, f"URL: {link_url}\n")

                # Insert buttons for the link and copying
                insert_link_buttons(details_textbox, link_url)
                details_textbox.insert(tk.END, "\n")

# Function to insert link and copy buttons
def insert_link_buttons(text_widget, url):
    link_button = ttk.Button(text_widget, text="Open Comment", cursor="hand2", command=lambda: open_link(url))
    text_widget.window_create(tk.END, window=link_button)
    details_textbox.insert(tk.END, " " * 1)

    copy_button = ttk.Button(text_widget, text="Copy Link", cursor="hand2", command=lambda: copy_to_clipboard(url))
    text_widget.window_create(tk.END, window=copy_button)
    details_textbox.insert(tk.END, "\n"+ "-" * 60 + "\n\n")

# Function to open a link in the default web browser
def open_link(url):
    webbrowser.open(url)

# Function to copy URL to clipboard
def copy_to_clipboard(url):
    pyperclip.copy(url)
    details_textbox.insert(tk.END, "Link copied to clipboard.\n")

# Main function to set up the GUI
def main():
    global root, result_textbox, details_textbox, calendar_start, calendar_end, reddit, status_label
    reddit=fetch_reddit_creds()
    rootx = ThemedTk(theme=theme.THEME_NAME)
    rootx.withdraw()
    root = tk.Toplevel(rootx)
    root.title("CMHoC Activity Checker")
    root.geometry("640x600")
    root.minsize(560, 480)
    logo = tk.PhotoImage(file="logos/logoorange.png", master=root)
    root.iconphoto(True, logo)

    theme.apply_theme(root)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    drop_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=drop_menu)
    drop_menu.add_command(label="Help", command=lambda: ActivityCheckHelpWindow(root))

    ttk.Label(root, text="Activity Checker", style="Heading.TLabel").pack(anchor="w", padx=16, pady=(14, 0))
    ttk.Label(
        root, text=theme.TOOL_DESCRIPTIONS["Activity Checker"], style="Subheading.TLabel"
    ).pack(anchor="w", padx=16, pady=(0, 8))

    # --- Date Range section ---
    date_frame = ttk.LabelFrame(root, text="Date Range", padding=10)
    date_frame.pack(fill="x", padx=16, pady=(0, 8))

    ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=(0, 6), pady=5, sticky="w")
    calendar_start = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendar_start.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")

    ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=(0, 6), pady=5, sticky="w")
    calendar_end = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendar_end.grid(row=0, column=3, padx=(0, 20), pady=5, sticky="w")

    check_button = ttk.Button(date_frame, text="Check Comments", command=run_check_comments)
    check_button.grid(row=0, column=4, pady=5)

    status_label = ttk.Label(root, text="", style="Subheading.TLabel")
    status_label.pack(anchor="w", padx=16, pady=(0, 8))

    # --- Results / Details panes ---
    panes = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    panes.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    results_frame = ttk.LabelFrame(panes, text="Results", padding=8)
    details_frame = ttk.LabelFrame(panes, text="Details", padding=8)
    panes.add(results_frame, weight=1)
    panes.add(details_frame, weight=2)

    result_textbox = tk.Listbox(results_frame)
    result_textbox.pack(fill="both", expand=True)
    result_textbox.bind('<<ListboxSelect>>', display_user_details)

    details_textbox = tk.Text(details_frame, wrap=tk.WORD)
    details_textbox.pack(fill="both", expand=True)
    details_textbox.tag_config("link", foreground="blue", underline=True)

    rootx.mainloop()

if __name__ == "__main__":
    main()
