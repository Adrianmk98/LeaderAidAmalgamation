import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import datetime

#Opens the window that shows allows for the user to select recent posts
def open_recent_posts_window(root,reddit,entry_link):
    recent_window = tk.Toplevel(root)
    recent_window.title("Load Recent Posts")

    # Label for slider
    slider_label = tk.Label(recent_window, text="Select number of days:")
    slider_label.pack(pady=10)

    # Slider for selecting the number of days
    days_slider = tk.Scale(recent_window, from_=1, to=30, orient=tk.HORIZONTAL)
    days_slider.set(7)  # Default to 7 days
    days_slider.pack(pady=10)

    # Frame for the posts and buttons
    frame = tk.Frame(recent_window)
    frame.pack(pady=10)

    # Treeview for displaying post titles and dates
    columns = ('Title', 'Date')
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
    tree.heading('Title', text='Post Title')
    tree.heading('Date', text='Date')

    tree.column('Title', width=300)
    tree.column('Date', width=150)

    tree.pack(side='left')

    # Scrollbar for the treeview
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

#Gets all posts from x subreddit for the last x days
    def fetch_recent_posts(reddit, days):
        subreddit = reddit.subreddit('cmhocvote')
        recent_posts = []
        time_limit = datetime.datetime.utcnow() - datetime.timedelta(days=days)  # Use datetime.datetime

        for submission in subreddit.new(limit=100):  # Fetch recent 100 posts
            submission_time = datetime.datetime.utcfromtimestamp(submission.created_utc)
            if submission_time >= time_limit:
                recent_posts.append((submission.title, submission.created_utc, submission.url))

        return recent_posts

    # Button to load posts based on slider value
    def load_posts():
        days = days_slider.get()
        posts = fetch_recent_posts(reddit, days)

        # Clear any existing entries in the treeview
        tree.delete(*tree.get_children())

        # Insert the recent posts into the treeview
        for post in posts:
            post_title = post[0]
            post_date = datetime.datetime.utcfromtimestamp(post[1]).strftime('%Y-%m-%d')  # Use datetime.datetime
            post_url = post[2]
            tree.insert('', 'end', values=(post_title, post_date), tags=(post_url,))

    load_button = tk.Button(recent_window, text="Load Recent Posts", command=load_posts)
    load_button.pack(pady=10)


    # Function to handle post selection and confirmation
    def preview_selected_post(entry_link):
        selected_item = tree.selection()
        if selected_item:
            post_values = tree.item(selected_item, 'values')
            post_title, post_date = post_values[0], post_values[1]
            post_url = tree.item(selected_item, 'tags')[0]  # Retrieve the URL stored in the tags
            populate_link_from_recent(post_url,entry_link)
            recent_window.destroy()

    confirm_button = tk.Button(recent_window, text="Preview Selected Post", command=lambda:preview_selected_post(entry_link))
    confirm_button.pack(pady=10)

def populate_link_from_recent(selected_link,entry_link):
    entry_link.delete(0, tk.END)  # Clear existing link
    entry_link.insert(0, selected_link)  # Insert the new selected link