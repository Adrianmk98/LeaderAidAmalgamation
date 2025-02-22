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

from dropDown.helpWindow import ActivityCheckHelpWindow
from config.getRedditCreds import fetch_reddit_creds

'''

 Program Purpose: Creates a gui which allows for input of a start date, and end date for the comment search. 
 The reddit API will search all posts in the indicated subreddit with certain flairs in order to determine which players from players.txt have sufficient activity.

 '''

# List of specific flairs to check in cmhoc since any other flairs do not qualify
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

# Function to read usernames from names.txt and filter out "Vacant" and "Party List MP Party" lines
def load_usernames_and_parties():
    users_and_parties = []
    with open("playerFiles/players.txt", 'r') as file:
        for line in file:
            clean_line = line.strip()
            # Skip empty lines or lines with "vacant" in any field
            if clean_line == "" or "vacant" in clean_line.lower():
                continue
            parts = clean_line.split('\t')
            # Ensure the line has at least 3 parts and ends with "Incumbent"
            if len(parts) >= 3 and parts[-1] == "Incumbent":
                username = parts[0]   # First column is the username
                party = parts[2]      # Third column is the party
                users_and_parties.append((username, party))
    return users_and_parties

# Function to check comments within time period
def check_comments():
    global user_found
    subreddit = "cmhoc"
    result_textbox.delete(0, tk.END)
    details_textbox.delete(1.0, tk.END)
    result_textbox.insert(tk.END, "Checking comments, please wait...\n")
    try:
        start_time = time.mktime(calendar_start.get_date().timetuple())
        end_time = time.mktime(calendar_end.get_date().timetuple())
        post_start_time = start_time - 5 * 24 * 3600 #-5 so it applies to EST
        post_end_time = end_time + 5 * 24 * 3600
        usernames_and_parties = load_usernames_and_parties()
        if not usernames_and_parties:
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
        for username, party in usernames_and_parties:
            if user_found[username]:
                result_textbox.insert(tk.END, f"{username} ({party}) - Comments found\n")
                result_textbox.itemconfig(tk.END, {'fg': 'green'})
            else:
                result_textbox.insert(tk.END, f"{username} ({party}) - No comments\n")
                result_textbox.itemconfig(tk.END, {'fg': 'red'})
        result_textbox.insert(tk.END, "Check complete.\n")
    except Exception as e:
        result_textbox.insert(tk.END, f"Error during comment checking: {e}\n")
        result_textbox.itemconfig(tk.END, {'fg': 'red'})

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
    link_button = tk.Button(text_widget, text="Open Comment", fg="blue", cursor="hand2",
                            command=lambda: open_link(url), relief=tk.FLAT)
    text_widget.window_create(tk.END, window=link_button)
    details_textbox.insert(tk.END, " " * 1)

    copy_button = tk.Button(text_widget, text="Copy Link", fg="black", cursor="hand2",
                            command=lambda: copy_to_clipboard(url), relief=tk.FLAT)
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
    global root, result_textbox, details_textbox, calendar_start, calendar_end,reddit
    reddit=fetch_reddit_creds()
    rootx = tk.Tk()
    rootx.withdraw()
    root = tk.Toplevel()
    root.title("CMHoC Activity Checker")
    logo = tk.PhotoImage(file="logos/logoorange.png")
    root.iconphoto(True, logo)
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    drop_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=drop_menu)
    drop_menu.add_command(label="Help", command=lambda: ActivityCheckHelpWindow(root))
    tk.Label(root, text="Start Date:").grid(row=0, column=0, padx=10, pady=5)
    calendar_start = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendar_start.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(root, text="End Date:").grid(row=1, column=0, padx=10, pady=5)
    calendar_end = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    calendar_end.grid(row=1, column=1, padx=10, pady=5)
    check_button = ttk.Button(root, text="Check Comments", command=run_check_comments)
    check_button.grid(row=2, column=0, columnspan=2, pady=10)
    result_textbox = tk.Listbox(root, width=50, height=15)
    result_textbox.grid(row=3, column=0, columnspan=2, pady=10)
    result_textbox.bind('<<ListboxSelect>>', display_user_details)
    details_textbox = tk.Text(root, width=60, height=15)
    details_textbox.grid(row=4, column=0, columnspan=2, pady=10)
    details_textbox.tag_config("link", foreground="blue", underline=True)
    root.mainloop()

if __name__ == "__main__":
    main()