import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import regex as re
import datetime
import pytz
import configparser

from VoteAnalyzer.recentPostLoader import open_recent_posts_window
from VoteAnalyzer.sortingData import sort_by_party, sort_breakdown_box
from config.getRedditCreds import fetch_reddit_creds
from dropDown.helpWindow import VoteAnalyzerHelpWindow
from VoteAnalyzer.VAplayerLoader import load_player_data


#Gets vote information and compares it to aye nay and abstention patterns with a margin of error
def analyze_votes(submission, player_data):
    votes = {}
    all_votes = {}
    non_voters = set(player_data.keys())  # To track MPs who haven't voted
    party_breakdown = {}

    # Compile regex patterns for vote counting
    aye_pattern = re.compile(r'\b(aye|oui|yea|pour){e<=1}\b', re.IGNORECASE)
    nay_pattern = re.compile(r'\b(nay|non|contre){e<=1}\b', re.IGNORECASE)
    abstain_pattern = re.compile(r'\b(abstain|abstention){e<=3}\b', re.IGNORECASE)

    # Get the submission date in UTC and convert it to EST
    submission_date_utc = datetime.datetime.utcfromtimestamp(submission.created_utc)
    utc_zone = pytz.utc
    est_zone = pytz.timezone("America/New_York")

    # Localize the UTC time and convert to EST
    submission_date = utc_zone.localize(submission_date_utc).astimezone(est_zone)
    current_time = datetime.datetime.now(est_zone)  # Current time in EST
    submission.comments.replace_more(limit=None)

    # Dictionary to store the most relevant instance for each MP
    relevant_mp = {}

    # Determine the most relevant instance of each MP based on date
    for name, mp_data in player_data.items():
        most_relevant_entry = None
        most_relevant_start_date = None

        for entry in mp_data:  # Iterate through each entry for the name
            start_date_str = entry.get("date")
            end_date_str = entry.get("status")

            try:
                # Parse start date and localize to EST
                start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y").replace(tzinfo=est_zone)
                end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y").replace(tzinfo=est_zone) if end_date_str != "Incumbent" else None

                # Store only if the MP was in office during the submission date
                if (start_date <= submission_date) and (end_date is None or end_date >= submission_date):
                    # Find the most relevant entry based on the start date
                    if most_relevant_start_date is None or start_date < most_relevant_start_date:
                        most_relevant_start_date = start_date
                        most_relevant_entry = entry

            except ValueError:
                try:
                    # Fallback to MM/DD/YYYY format if the first attempt fails
                    start_date = datetime.datetime.strptime(start_date_str, "%m/%d/%Y").replace(tzinfo=est_zone)
                    end_date = datetime.datetime.strptime(end_date_str, "%m/%d/%Y").replace(tzinfo=est_zone) if end_date_str != "Incumbent" else None

                    # Store only if the MP was in office during the submission date
                    if (start_date <= submission_date) and (end_date is None or end_date >= submission_date):
                        # Find the most relevant entry based on the start date
                        if most_relevant_start_date is None or start_date < most_relevant_start_date:
                            most_relevant_start_date = start_date
                            most_relevant_entry = entry
                except ValueError as e:
                    print(f"Date parsing error for {name}: {e}")

        # Store the most relevant entry if found
        if most_relevant_entry:
            relevant_mp[name] = most_relevant_entry

    for comment in submission.comments.list():
        author = comment.author.name.lower() if comment.author else None
        submission_age_days = (current_time - submission_date).days

        if author and (author in relevant_mp):
            comment_text = comment.body
            all_votes[author] = (comment_text, relevant_mp.get(author, ('Unknown', 'Indy')))

            if author in relevant_mp:
                # Retrieve MP data from the relevant instance
                mp_data = relevant_mp[author]
                riding = mp_data.get("riding", "Unknown")
                party = mp_data.get("party", "Indy")

                comment_text_lower = comment_text.lower()

                # Count votes based on comment text
                if aye_pattern.search(comment_text_lower):
                    votes[author] = ('aye', riding, party, comment.created_utc)
                    party_breakdown[party] = party_breakdown.get(party, 0) + 1
                elif nay_pattern.search(comment_text_lower):
                    votes[author] = ('nay', riding, party, comment.created_utc)
                    party_breakdown[party] = party_breakdown.get(party, 0) + 1
                elif abstain_pattern.search(comment_text_lower):
                    votes[author] = ('abstain', riding, party, comment.created_utc)

    # Calculate all_mps and voted_mps
    all_mps = set(relevant_mp.keys())  # Only consider MPs who were in office
    voted_mps = set(votes.keys())

    # Determine non-voters
    non_voters = all_mps - voted_mps

    # Final vote tally
    final_votes = {}
    for author, (vote_type, riding, party, timestamp) in votes.items():
        if author not in final_votes or final_votes[author][3] < timestamp:
            final_votes[author] = (vote_type, riding, party, timestamp)

    return final_votes, all_votes, non_voters


def display_vote_breakdown(final_votes, all_votes, player_data, vacant_count, submission):
    # Clear the text box
    breakdown_box.config(state=tk.NORMAL)  # Enable editing to insert text
    breakdown_box.delete(1.0, tk.END)

    # Tally the votes
    tally = {'Aye': 0, 'Nay': 0, 'Abstain': 0}
    party_tally = {}
    no_longer_mps = {}  # For those who voted but are no longer in player_data

    # Initialize party tally structure
    for mp_data_list in player_data.values():
        for mp_data in mp_data_list:
            party = mp_data.get("party", "Indy")
            if party not in party_tally:
                party_tally[party] = {'Aye': 0, 'Nay': 0, 'Abstain': 0, 'No Vote': 0}

    # Detailed Breakdown with Line Highlighting for those who voted
    for author, (comment_text, player_info) in all_votes.items():
        riding = player_info.get("riding", "Unknown")
        party = player_info.get("party", "Indy")
        vote_type = final_votes.get(author, [None])[0]
        line_text = f"({riding})\t{author.capitalize()} [{party}]: {comment_text}\n"

        if author in player_data:
            # Highlight vote types
            if vote_type == 'aye':
                breakdown_box.insert(tk.END, line_text, 'green_bg')
                tally['Aye'] += 1
                party_tally[party]['Aye'] += 1
            elif vote_type == 'nay':
                breakdown_box.insert(tk.END, line_text, 'red_bg')
                tally['Nay'] += 1
                party_tally[party]['Nay'] += 1
            elif vote_type == 'abstain':
                breakdown_box.insert(tk.END, line_text, 'yellow_bg')
                tally['Abstain'] += 1
                party_tally[party]['Abstain'] += 1
            else:
                breakdown_box.insert(tk.END, f"{line_text.strip()} - No Vote\n", 'no_vote_bg')
        else:
            continue

    # Tally votes from final_votes
    tally_box.delete(1.0, tk.END)
    tally_text = "\nTally of Votes:\n"

    # Calculate eligible voters
    eligible_count = 0
    eligible_non_voters = []  # List of eligible MPs who haven't voted

    # Set the UTC timezone for the submission date
    utc_zone = pytz.utc
    est_zone = pytz.timezone("America/New_York")
    submission_date_utc = datetime.datetime.utcfromtimestamp(submission.created_utc)
    submission_date_utc = utc_zone.localize(submission_date_utc).astimezone(est_zone)
    submission_date_est = submission_date_utc.date()  # Use only the date

    # Check each MP in player_data for eligibility
    for name, mp_data_list in player_data.items():
        for mp_data in mp_data_list:  # Iterate over each instance of the MP
            start_date_str = mp_data.get("date")  # Original entry date
            end_date_str = mp_data.get("status")  # End date

            try:
                # Parse start date as a date (no timezone)
                start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y").date()

                # Parse end date as a date or set to None for incumbents
                if end_date_str == "Incumbent":
                    end_date = None  # No end date for incumbents
                else:
                    end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y").date()

                # Count as eligible if the dates align with the submission date
                if (start_date <= submission_date_est) and (end_date is None or end_date >= submission_date_est):
                    eligible_count += 1
                    # Check if they haven't voted
                    if name not in final_votes:
                        eligible_non_voters.append((name, mp_data))  # Store eligible non-voter data
                        party = mp_data.get("party", "Indy")
                        party_tally[party]['No Vote'] += 1  # Count as a "No Vote" for the party
                    break  # No need to check other instances for this MP
            except ValueError as e:
                print(f"Date parsing error for {name}: {e}")

    # Number of people who haven't voted
    voted_people = set(final_votes.keys())
    not_voted = eligible_count - len(voted_people)

    breakdown_box.insert(tk.END, f"\n--- Number of people who haven't voted: {not_voted} out of {eligible_count} eligible voters ---\n", 'no_vote_bg')

    # Display eligible non-voters
    if eligible_non_voters:
        breakdown_box.insert(tk.END, "\n--- Eligible Non-Voters ---\n", 'no_vote_bg')
        for name, mp_data in eligible_non_voters:
            riding = mp_data.get("riding", "Unknown")
            party = mp_data.get("party", "Indy")
            breakdown_box.insert(tk.END, f"({riding})\t{name.capitalize()} [{party}]: No Vote\n", 'no_vote_bg')

    # Define text tags for color highlighting in the tally box
    tally_box.tag_configure('green_text', foreground='green')
    tally_box.tag_configure('red_text', foreground='red')

    # Party breakdown
    tally_text = "\nParty Breakdown:\n"
    # Initialize totals
    total_tally = {'Aye': 0, 'Nay': 0, 'Abstain': 0, 'No Vote': 0}

    # First, add all parties except FMR
    for party, counts in party_tally.items():
        if party != "FMR":  # Skip FMR for now
            tally_text += f"{party}: Aye: {counts['Aye']}, Nay: {counts['Nay']}, Abstain: {counts['Abstain']}, No Vote: {counts['No Vote']}\n"
            # Update total tally
            total_tally['Aye'] += counts['Aye']
            total_tally['Nay'] += counts['Nay']
            total_tally['Abstain'] += counts['Abstain']
            total_tally['No Vote'] += counts['No Vote']

    # Now, add FMR at the bottom
    if "FMR" in party_tally:
        counts = party_tally["FMR"]
        tally_text += f"FMR: Aye: {counts['Aye']}, Nay: {counts['Nay']}, Abstain: {counts['Abstain']}, No Vote: {counts['No Vote']}\n"
        # Update total tally for FMR
        total_tally['Aye'] += counts['Aye']
        total_tally['Nay'] += counts['Nay']
        total_tally['Abstain'] += counts['Abstain']
        total_tally['No Vote'] += counts['No Vote']

    # Determine if Aye or Nay is the highest in total tally and select highlight tag
    highlight_tag = 'green_text' if total_tally['Aye'] > total_tally['Nay'] else 'red_text'

    # Add the non-highlighted portion up to Total Tally
    tally_text += "\nTotal Tally:\n"
    tally_box.insert(tk.END, tally_text)

    # Insert the highlighted Total Tally values
    tally_box.insert(
        tk.END,
        f"Aye: {total_tally['Aye']}, Nay: {total_tally['Nay']}, Abstain: {total_tally['Abstain']}, No Vote: {total_tally['No Vote']}\n",
        highlight_tag
    )

    # Add eligible and non-voter counts
    tally_box.insert(tk.END, f"\nTotal Eligible Voters: {eligible_count}\n")
    tally_box.insert(tk.END, f"Number of people who haven't voted: {not_voted}\n")

    # Make the breakdown read-only after updating it
    breakdown_box.config(state=tk.DISABLED)

def toggle_editable():
    if entry_link["state"] == "normal":
        entry_link.config(state="readonly")
        toggle_button.config(text="❌")  # X emoji for non-editable
    else:
        entry_link.config(state="normal")
        toggle_button.config(text="✅")  # Checkmark emoji for editable

def addNormalize(PLAYER_DATA_FILE):
    # Button to trigger analysis
    analyze_button = tk.Button(root, text="Normalize", command=lambda: analyze_votes_gui(PLAYER_DATA_FILE))
    analyze_button.grid(row=3, column=1, padx=10, pady=(5, 10))


def analyze_votes_gui(PLAYER_DATA_FILE):
    reddit_link = entry_link.get()  # Get the Reddit link from the input box
    toggle_editable()
    # Load player data from the fixed player file
    player_data, vacant_count = load_player_data()

    # Get the Reddit submission from the link
    submission = reddit.submission(url=reddit_link)

    # Parse the submission date in UTC
    submission_date_utc = datetime.datetime.utcfromtimestamp(submission.created_utc)

    # Convert UTC to EST
    utc_zone = pytz.utc
    est_zone = pytz.timezone("America/New_York")
    submission_date_est = utc_zone.localize(submission_date_utc).astimezone(est_zone)

    # Format the date in EST
    formatted_date = submission_date_est.strftime("%A, %B %d, %Y")  # Format the date
    submission.formatted_date = formatted_date  # Add formatted date as an attribute
    print(f"Submission Date (EST): {formatted_date}")  # Print the date in the console

    # Analyze votes
    final_votes, all_votes, non_voters = analyze_votes(submission, player_data)

    # Display the results and tally, passing old_players as well
    display_vote_breakdown(final_votes, all_votes, player_data, vacant_count, submission)

def main():
    global entry_link,breakdown_box
    global tally_box,window,reddit,root,toggle_button,entry_link
    # Fixed player data file (adjust the file path accordingly)
    config = configparser.ConfigParser()
    files_read = config.read('config/locationOfTxt.ini')
    PLAYER_DATA_FILE = config['player']['playerFile']
    rootx = tk.Tk()
    rootx.withdraw()  # Hide the root window
    root = tk.Toplevel()
    root.title("CMHoC Vote Analyzer")
    logo = tk.PhotoImage(file="logos/logoblue.png")
    root.iconphoto(True, logo)
    reddit = fetch_reddit_creds()
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    drop_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=drop_menu)
    drop_menu.add_command(label="Help", command=lambda: VoteAnalyzerHelpWindow(root))
    # Input box for Reddit link
    label_link = tk.Label(root, text="Enter Reddit Link:")
    label_link.grid(row=0, column=0, padx=10, pady=(10, 0))  # Position the label

    entry_link = tk.Entry(root, width=50)
    entry_link.grid(row=1, column=0, padx=10, pady=(0, 10))  # Position the entry

    # Button to trigger analysis
    analyze_button = tk.Button(root, text="Analyze Votes", command=lambda:analyze_votes_gui(PLAYER_DATA_FILE))
    analyze_button.grid(row=2, column=0, padx=10, pady=(0, 10))  # Position the button below the previous button


    # Text area for displaying the breakdown
    breakdown_box = scrolledtext.ScrolledText(root, width=80, height=30)
    breakdown_box.grid(row=3, column=0, padx=10, pady=(5, 10))  # Add padding for spacing

    # Toggle button to lock/unlock the entry, positioned right next to the link entry
    toggle_button = tk.Button(root, text="✅", command=toggle_editable, relief="flat")
    toggle_button.grid(row=0, column=1, padx=2, pady=5, sticky="w")

    # Text area for displaying the tally
    tally_box = scrolledtext.ScrolledText(root, width=60, height=20)
    tally_box.grid(row=4, column=0, padx=10, pady=(5, 10))  # Add padding for spacing

    # Button to open recent posts
    open_posts_button = tk.Button(root, text="Open Recent Posts",
                                  command=lambda: open_recent_posts_window(root, reddit, entry_link))
    open_posts_button.grid(row=0, column=2, padx=10, pady=(0, 5))  # Position the button below the entry

    sort_button = tk.Button(root, text="Sort by Vote Type", command=lambda: (addNormalize(PLAYER_DATA_FILE), sort_breakdown_box(breakdown_box)))
    sort_button.grid(row=1, column=2, padx=10, pady=(5, 10))  # Add padding for spacing

    sort_party_button = tk.Button(root, text="Sort by Party Affiliation", command=lambda: (addNormalize(PLAYER_DATA_FILE), sort_by_party(breakdown_box)))
    sort_party_button.grid(row=2, column=2, padx=10, pady=(5, 10))

    # Define tag styles for highlighting
    breakdown_box.tag_config('green_bg', background='lightgreen')
    breakdown_box.tag_config('red_bg', background='lightcoral')
    breakdown_box.tag_config('yellow_bg', background='lightyellow')
    breakdown_box.tag_config('no_vote_bg', background='lightgray')

    root.mainloop()

if __name__ == "__main__":
    main()