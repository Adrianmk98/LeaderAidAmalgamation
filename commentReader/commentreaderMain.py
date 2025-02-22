import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import difflib
import re
from ttkthemes import ThemedTk
from datetime import datetime, timedelta

from commentReader.CRplayerLoader import load_usernames
from dropDown.helpWindow import CommentReaderHelpWindow
from config.getRedditCreds import fetch_reddit_creds

#Fetches recent posts from 'cmhoc' subreddit within the past number of days.
def fetch_recent_posts(reddit,days):

    subreddit = reddit.subreddit('cmhoc')
    recent_posts = []
    time_limit = datetime.utcnow() - timedelta(days=days)

    for submission in subreddit.new(limit=100):  # Fetch recent 100 posts
        submission_time = datetime.utcfromtimestamp(submission.created_utc)
        if submission_time >= time_limit:
            recent_posts.append((submission.title, submission.created_utc, submission.url))

    return recent_posts
#Enters the selected link as the chosen link in the GUI
def populate_link_from_recent(selected_link):
    link_entry.delete(0, tk.END)  # Clear existing link
    link_entry.insert(0, selected_link)  # Insert the new selected link

#Opens a new window with a slider to select recent posts from the designated subreddit.
def open_recent_posts_window(event=None):
    recent_window = tk.Toplevel(root)
    recent_window.title("Load Recent Posts")

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

    # Button to load posts based on slider value
    def load_posts():
        days = days_slider.get()
        posts = fetch_recent_posts(reddit,days)

        # Clear any existing entries in the treeview
        tree.delete(*tree.get_children())

        # Insert the recent posts into the treeview
        for post in posts:
            post_title = post[0]
            post_date = datetime.utcfromtimestamp(post[1]).strftime('%Y-%m-%d')
            post_url = post[2]
            tree.insert('', 'end', values=(post_title, post_date), tags=(post_url,))

    load_button = tk.Button(recent_window, text="Load Recent Posts", command=load_posts)
    load_button.pack(pady=10)

    # Function to handle post selection and confirmation
    def preview_selected_post():
        selected_item = tree.selection()
        if selected_item:
            post_values = tree.item(selected_item, 'values')
            post_title, post_date = post_values[0], post_values[1]
            post_url = tree.item(selected_item, 'tags')[0]  # Retrieve the URL stored in the tags
            populate_link_from_recent(post_url)
            recent_window.destroy()

    # Button to confirm the selected post
    confirm_button = tk.Button(recent_window, text="Preview Selected Post", command=preview_selected_post)
    confirm_button.pack(pady=10)

def find_close_matches(word, text, max_distance=3):
    words_in_text = text.split()
    matches = []
    for index, text_word in enumerate(words_in_text):
        if difflib.SequenceMatcher(None, word, text_word).ratio() >= (1 - max_distance / len(word)):
            start = text.find(text_word)
            end = start + len(text_word)
            matches.append((start, end))
    return matches

def fetch_comments(reddit_link):
    try:
        submission = reddit.submission(url=reddit_link)
        submission.comments.replace_more(limit=None)
        comments = submission.comments.list()
        toggle_editable()
        return submission, comments  # Return both submission and comments
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch comments: {e}")
        return None, []


def display_comments(comments):
    user_comments = {}
    for comment in comments:
        author = str(comment.author) if comment.author else "Deleted"
        # Ignore comments by AutoModerator
        if author == "AutoModerator":
            continue
        if author not in user_comments:
            user_comments[author] = []
        user_comments[author].append(comment)
    return user_comments


def update_users(event=None):
    selected_user = user_dropdown.get()
    comments_list.delete(0, tk.END)

    # Clear the comment display when switching users
    comment_display.config(state=tk.NORMAL)
    comment_display.delete(1.0, tk.END)
    comment_display.config(state=tk.DISABLED)

    if selected_user in user_comments:
        for i, comment in enumerate(user_comments[selected_user]):
            read_status = 'read' if selected_user in read_comments and i in read_comments[selected_user] else 'unread'
            display_text = f"{i + 1}. {comment.body[:50]}... ({read_status})"
            comments_list.insert(tk.END, display_text)

        # Automatically select and display the first comment
        if user_comments[selected_user]:
            comments_list.selection_set(0)  # Select the first comment
            update_comments(None)


def update_comments(event=None):
    selected_user = user_dropdown.get()
    selected_index = comments_list.curselection()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]
        comment = user_comments[selected_user][comment_index]

        # Ensure you're accessing the comment's body (the actual text)
        if hasattr(comment, 'body'):
            comment_body = comment.body
            comment_id = comment.id  # Assuming comment has an ID attribute
        else:
            comment_body = str(comment)  # Fallback if comment is already a string
            comment_id = hash(comment_body)  # Use a hash of the comment text as a fallback ID

        # Remove escaped underscores in the comment body
        comment_body = comment_body.replace('\\_', '_')

        comment_display.config(state=tk.NORMAL)
        comment_display.delete(1.0, tk.END)
        comment_display.insert(tk.END, comment_body)

        lower_comment_body = comment_body.lower()

        # Highlight usernames
        for username in load_usernames():
            # Use re.escape to safely handle special characters in the username
            escaped_username = re.escape(username)
            if re.search(rf'\b{escaped_username}\b', lower_comment_body):
                start = lower_comment_body.find(username.lower())
                end = start + len(username)
                comment_display.tag_add("username", f"1.0 + {start} chars", f"1.0 + {end} chars")
                comment_display.tag_configure("username", foreground="blue")

        # Perform unparliamentary language check
        for unparliamentary_word in unparliamentary_words:
            if unparliamentary_word in lower_comment_body:
                start = lower_comment_body.find(unparliamentary_word)
                end = start + len(unparliamentary_word)
                comment_display.tag_add("unparliamentary", f"1.0 + {start} chars", f"1.0 + {end} chars")
                comment_display.tag_configure("unparliamentary", foreground="red")

        # Highlight the entire comment in green if it's marked as read
        if selected_user in read_comments and comment_index in read_comments[selected_user]:
            comment_display.tag_add("read", "1.0", tk.END)
            comment_display.tag_configure("read", background="lightgreen")

        comment_display.config(state=tk.DISABLED)



def mark_as_read(event=None):
    selected_index = comments_list.curselection()
    selected_user = user_dropdown.get()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]

        # Mark the comment as read
        if selected_user not in read_comments:
            read_comments[selected_user] = set()
        read_comments[selected_user].add(comment_index)

        # Call update_users(None) to refresh the user display
        update_users(None)

        # Restore the selection of the comment
        comments_list.selection_clear(0, tk.END)
        comments_list.selection_set(comment_index)
        comments_list.activate(comment_index)  # Ensure the same comment stays active
        comments_list.see(comment_index)  # Scroll to the comment if necessary

        # Ensure the top text box updates with the correct comment
        update_comments(None)


def open_in_browser(event=None):
    selected_user = user_dropdown.get()
    selected_index = comments_list.curselection()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]
        comment = user_comments[selected_user][comment_index]

        # Get the permalink for the selected comment and open it in the browser
        comment_link = f"https://reddit.com{comment.permalink}"
        webbrowser.open(comment_link)

def fetch_and_display(event=None):
    reddit_link = link_entry.get()
    submission, comments = fetch_comments(reddit_link)
    global user_comments
    user_comments = display_comments(comments)

    if user_comments:
        user_dropdown['values'] = list(user_comments.keys())
        user_dropdown.current(0)  # Select the first user by default
        update_users(None)  # Update the comment list for the first user
    else:
        messagebox.showinfo("No comments", "No comments were fetched.")


def move_to_next_user(event=None):
    # Get the current selected user
    current_index = user_dropdown.current()
    user_count = len(user_dropdown['values'])

    # Move to the next user, looping back to the first if at the end
    next_index = (current_index + 1) % user_count
    user_dropdown.current(next_index)

    # Update the user selection and comments display
    update_users(None)

    # Prevent the default behavior of tabbing out of the widget
    return "break"

# Function to move to the next comment by the same user
def move_to_next_comment(event=None):
    selected_user = user_dropdown.get()
    selected_index = comments_list.curselection()

    if selected_user in user_comments and selected_index:
        current_index = selected_index[0]
        next_index = (current_index + 1) % len(user_comments[selected_user])  # Wrap around if at the end

        # Select the next comment
        comments_list.selection_clear(0, tk.END)  # Clear previous selection
        comments_list.selection_set(next_index)   # Select the next comment
        comments_list.activate(next_index)        # Ensure the selection is visible
        comments_list.see(next_index)             # Scroll to the selected comment

        update_comments(None)  # Update the comment display with the new selection

def toggle_editable(event=None):
    if link_entry["state"] == "normal":
        link_entry.config(state="readonly")
        toggle_button.config(text="❌")  # X emoji for non-editable
    else:
        link_entry.config(state="normal")
        toggle_button.config(text="✅")  # Checkmark emoji for editable

def keybindsopening():
    #from Comment_parser.dropdown.keybinds import open_keybinds_window
    open_keybinds_window(root)

def open_help_window():
    """Opens a help window that dynamically displays keybinds."""
    help_window = tk.Toplevel(root)
    help_window.title("Help")

    # Create a dynamic help message from keybindings
    help_message = "Keybindings:\n"
    help_message += "\n".join(f"- {key}: {action}" for action, key in keybindings.items())

    tk.Label(help_window, text=help_message, justify=tk.LEFT, padx=10, pady=10).pack()

def open_keybinds_window(root):
    """Opens a window to set keybindings."""
    keybind_window = ThemedTk(theme="yaru")
    keybind_window.title("Set Keybinds")

    # Label and dropdown for selecting an action to change the keybind
    tk.Label(keybind_window, text="Select Action:").grid(row=0, column=0, padx=10, pady=5)
    action_dropdown = ttk.Combobox(keybind_window, values=list(keybindings.keys()), state="readonly")
    action_dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Display current keybind and capture next key press
    tk.Label(keybind_window, text="Press New Key:").grid(row=1, column=0, padx=10, pady=5)
    key_display = tk.Entry(keybind_window, width=20, state="readonly")
    key_display.grid(row=1, column=1, padx=10, pady=5)

    # To store the selected keybinding
    new_keybind = tk.StringVar()

    def record_key(event):
        """Capture key press with optional modifiers."""
        modifier = ""
        if event.state & 0x0004:  # Check for Control
            modifier = "Control-"
        elif event.state & 0x0001:  # Check for Shift
            modifier = "Shift-"
        elif event.state & 0x0008:  # Check for Alt
            modifier = "Alt-"
        new_key = f"{modifier}{event.keysym}"
        new_keybind.set(new_key)
        key_display.config(state="normal")
        key_display.delete(0, tk.END)
        key_display.insert(0, new_key)
        key_display.config(state="readonly")

    key_display.bind("<KeyPress>", record_key)  # Listen for key press events

    def reset_key():
        """Clear the key display for new input."""
        new_keybind.set("")
        key_display.config(state="normal")
        key_display.delete(0, tk.END)
        key_display.config(state="readonly")

    # Reset button
    reset_button = tk.Button(keybind_window, text="Reset", command=reset_key)
    reset_button.grid(row=1, column=2, padx=10, pady=5)

    def save_keybind():
        action = action_dropdown.get()
        new_key = new_keybind.get()

        if action and new_key:
            # Unbind the previous key
            old_key = keybindings[action]
            root.unbind(f"<{old_key}>")

            # Bind the new key to the corresponding action
            if action == "Next User":
                root.bind(f"<{new_key}>", move_to_next_user)
            elif action == "Next Comment":
                root.bind(f"<{new_key}>", move_to_next_comment)
            elif action == "Load Recent Posts":
                root.bind(f"<{new_key}>", open_recent_posts_window)
            elif action == "Fetch Comments":
                root.bind(f"<{new_key}>", fetch_and_display())
            elif action == "Open in Browser":
                root.bind(f"<{new_key}>", open_in_browser)
            elif action == "Mark Read":
                root.bind(f"<{new_key}>", mark_as_read)

            # Update the keybindings dictionary
            keybindings[action] = new_key
            messagebox.showinfo("Keybind Set", f"{action} is now bound to {new_key}")
            keybind_window.destroy()

    # Save button
    save_button = tk.Button(keybind_window, text="Save Keybind", command=save_keybind)
    save_button.grid(row=2, column=1, padx=10, pady=5)

def main():
    global root, link_label, link_entry, fetch_button, user_label,user_dropdown,comments_list,comments_label,comments_dropdown,scrollbar,comment_display,read_button
    global user_comments,read_comments,unparliamentary_words,checked_comments,keybindings,toggle_button,reddit
    # GUI setup
    user_comments = {}
    checked_comments = {}
    read_comments = {}
    reddit=fetch_reddit_creds()
    # Create the main Tk window

    rootx = tk.Tk()
    rootx.withdraw()
    root = tk.Toplevel()
    root.title("CMHoC Comments Reader")
    logo = tk.PhotoImage(file="logos/logoblue.png")
    root.iconphoto(True, logo)

    # Create a menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Load unparliamentary words from 'unparliamentary.txt' using utf-8 encoding
    with open('CommentReader/unparliamentary.txt', 'r', encoding='utf-8') as file:
        unparliamentary_words = [line.strip().lower() for line in file]

    # Load usernames from 'players.txt' and add them to the unparliamentary_words list
    with open('playerFiles/players.txt', 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()
            if clean_line and "vacant" not in clean_line.lower() and not clean_line.startswith("Party List"):
                parts = clean_line.split('\t')
                if len(parts) >= 3 and parts[1].lower() != "vacant":
                    username = parts[1].strip().lower()
                    unparliamentary_words.append(username)

    # Input for Reddit link
    link_label = tk.Label(root, text="Enter Reddit Link:")
    link_label.grid(row=0, column=0, padx=10, pady=5)

    link_entry = tk.Entry(root, width=50)
    link_entry.grid(row=0, column=1, padx=(10, 0), pady=5)  # Adjust padding for spacing

    # Toggle button to lock/unlock the entry, positioned right next to the link entry
    toggle_button = tk.Button(root, text="✅", command=toggle_editable, relief="flat")
    toggle_button.grid(row=0, column=2, padx=(5, 10), pady=5)  # Add slight padding to separate from entry

    # Fetch comments button
    fetch_button = tk.Button(root, text="Fetch Comments", command=lambda: fetch_and_display())
    fetch_button.grid(row=0, column=3, padx=10, pady=5)

    # Dropdown for users
    user_label = tk.Label(root, text="Select User:", )
    user_label.grid(row=1, column=0, padx=10, pady=5)

    user_dropdown = ttk.Combobox(root, state="readonly")
    user_dropdown.bind("<<ComboboxSelected>>", update_users)
    user_dropdown.grid(row=1, column=1, padx=10, pady=5)

    # Listbox for comments
    comments_list = tk.Listbox(root, width=80, height=10)
    comments_list.grid(row=2, column=0, columnspan=3, padx=10, pady=5)
    comments_list.bind("<<ListboxSelect>>", update_comments)

    # Scrollbar for comment display
    scrollbar = tk.Scrollbar(root)
    scrollbar.grid(row=3, column=3, sticky='ns')

    # Text widget to display selected comment
    comment_display = tk.Text(root, wrap=tk.WORD, width=80, height=15, yscrollcommand=scrollbar.set, state=tk.DISABLED)
    comment_display.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

    scrollbar.config(command=comment_display.yview)

    # Button to mark as read
    read_button = tk.Button(root, text="Mark as Read", command=mark_as_read)
    read_button.grid(row=4, column=1, padx=10, pady=5, sticky='w')

    # Button to open the comment in the browser
    browser_button = tk.Button(root, text="Open in Browser", command=open_in_browser)
    browser_button.grid(row=4, column=1, padx=10, pady=5, sticky='e')

    # Button to load recent posts
    load_recent_button = tk.Button(root, text="Load Recent Posts", command=open_recent_posts_window)
    load_recent_button.grid(row=1, column=3, padx=10, pady=5)

    user_comments = {}
    checked_comments = {}
    read_comments = {}
    drop_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=drop_menu)
    drop_menu.add_command(label="Keybind Settings", command=keybindsopening)
    drop_menu.add_command(label="Help", command=lambda: CommentReaderHelpWindow(root,keybindings))
    keybindings = {
        "Next User": "Control-u",
        "Next Comment": "Control-n",
        "Load Recent Posts": "Control-r",
        "Fetch Comments": "Return",
        "Open in Browser": "Control-b",
        "Mark Read": "Control-m"
    }

    # Example keybindings
    root.bind("<Control-u>", move_to_next_user)
    root.bind("<Control-n>", move_to_next_comment)
    root.bind("<Control-r>", open_recent_posts_window)
    root.bind("<Return>", fetch_and_display)
    root.bind("<Control-b>", open_in_browser)
    root.bind("<Control-m>", mark_as_read)

if __name__ == "__main__":
    main()