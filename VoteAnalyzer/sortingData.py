import tkinter as tk
import regex as re

original_lines = []
def load_original_lines(breakdown_box):
    global original_lines
    original_lines.clear()  # Clear previous entries
    line_start = "1.0"
    while True:
        line_end = breakdown_box.index(f"{line_start} lineend")
        line_text = breakdown_box.get(line_start, line_end)

        if not line_text.strip():
            break  # Stop if we reach an empty line (end of content)

        # Capture tags for highlighting
        tags = breakdown_box.tag_names(line_start)
        vote_type = None
        if 'green_bg' in tags:
            vote_type = 'Aye'
        elif 'red_bg' in tags:
            vote_type = 'Nay'
        elif 'yellow_bg' in tags:
            vote_type = 'Abstain'
        elif 'no_vote_bg' in tags:
            vote_type = 'No Vote'

        # Store line with its vote type and text
        original_lines.append((line_text, vote_type))
        print(line_text)
        line_start = breakdown_box.index(f"{line_start}+1line")

def sort_by_party(breakdown_box):
    if not original_lines:
        load_original_lines(breakdown_box)

    lines_with_tags = []
    for line_text, vote_type in original_lines:
        try:
            # Find first occurrence of '(' and start searching after it
            first_open = line_text.index("[")
            second_open = line_text.index("[", first_open + 1)

            # Find the corresponding closing ']'
            second_close = line_text.index("]", second_open)

            # Extract text inside the second pair of parentheses
            party_affiliation = line_text[second_open + 1: second_close]
        except ValueError:
            party_affiliation = "Unk"

        lines_with_tags.append((line_text, party_affiliation, vote_type))

    # Sort lines based on party affiliation
    sorted_lines = sorted(lines_with_tags, key=lambda line: line[1])

    breakdown_box.config(state=tk.NORMAL)
    breakdown_box.delete(1.0, tk.END)

    previous_party = None
    for line_text, party, vote_type in sorted_lines:
        # Insert a line separator if the party changes
        if party != previous_party:
            if previous_party is not None:  # Don't insert a line before the first party
                breakdown_box.insert(tk.END, "-" * 80 + "\n")  # Insert separator line
            breakdown_box.insert(tk.END, f"{party}:\n")  # Insert party header
            previous_party = party  # Update the previous party

        # Insert the entry
        start_idx = breakdown_box.index(tk.END)
        breakdown_box.tag_configure('green_bg', background='lightgreen')
        breakdown_box.tag_configure('red_bg', background='lightcoral')
        breakdown_box.tag_configure('yellow_bg', background='lightyellow')

        print(vote_type,"BADWOLF")
        if vote_type == 'Aye':
            breakdown_box.insert(tk.END, line_text+ "\n", 'green_bg')
        elif vote_type == 'Nay':
            breakdown_box.insert(tk.END, line_text+ "\n", 'red_bg')
        elif vote_type == 'Abstain':
            breakdown_box.insert(tk.END, line_text+ "\n", 'yellow_bg')

        #breakdown_box.insert(tk.END, line_text + "\n")
        end_idx = breakdown_box.index(tk.END)

        # Highlight the vote type if it's found
        if vote_type and vote_type in line_text:  # Check if vote_type exists in line_text
            vote_start = line_text.rindex(vote_type)
            vote_end = vote_start + len(vote_type)
            vote_tag_start = f"{start_idx}+{vote_start}c"
            vote_tag_end = f"{start_idx}+{vote_end}c"
            breakdown_box.tag_add(vote_type.lower(), vote_tag_start, vote_tag_end)

    breakdown_box.config(state=tk.DISABLED)

def sort_by_govPosition(breakdown_box):
    if not original_lines:
        load_original_lines(breakdown_box)

    lines_with_tags = []
    for line_text, vote_type in original_lines:
        try:
            party_start = line_text.index("[") + 1
            party_end = line_text.index("]")
            position_affiliation = line_text[party_start:party_end]
        except ValueError:
            position_affiliation = "Unk"

        lines_with_tags.append((line_text, position_affiliation, vote_type))

    # Sort lines based on party affiliation
    sorted_lines = sorted(lines_with_tags, key=lambda line: line[1])

    breakdown_box.config(state=tk.NORMAL)
    breakdown_box.delete(1.0, tk.END)

    previous_party = None
    for line_text, party, vote_type in sorted_lines:
        # Insert a line separator if the party changes
        if party != previous_party:
            if previous_party is not None:  # Don't insert a line before the first party
                breakdown_box.insert(tk.END, "-" * 80 + "\n")  # Insert separator line
            breakdown_box.insert(tk.END, f"{party}:\n")  # Insert party header
            previous_party = party  # Update the previous party

        # Insert the entry
        start_idx = breakdown_box.index(tk.END)
        breakdown_box.insert(tk.END, line_text + "\n")
        end_idx = breakdown_box.index(tk.END)

        # Highlight the vote type if it's found
        if vote_type and vote_type in line_text:  # Check if vote_type exists in line_text
            vote_start = line_text.rindex(vote_type)
            vote_end = vote_start + len(vote_type)
            vote_tag_start = f"{start_idx}+{vote_start}c"
            vote_tag_end = f"{start_idx}+{vote_end}c"
            breakdown_box.tag_add(vote_type.lower(), vote_tag_start, vote_tag_end)

    breakdown_box.config(state=tk.DISABLED)


def sort_breakdown_box(breakdown_box):
    aye_pattern = re.compile(r'\b(aye|oui|yea|pour|yes|yep|affirmative)\b', re.IGNORECASE)
    nay_pattern = re.compile(r'\b(nay|non|contre|no|nope|negative)\b', re.IGNORECASE)
    abstain_pattern = re.compile(r'\b(abstain|abstention|withhold|pass)\b', re.IGNORECASE)
    breakdown_box.tag_configure('green_bg', background='lightgreen')
    breakdown_box.tag_configure('red_bg', background='lightcoral')
    breakdown_box.tag_configure('yellow_bg', background='lightyellow')
    # Ensure original_lines is available
    if not original_lines:
        load_original_lines(breakdown_box)  # Load original lines if they are not available

    # Determine vote type using regex patterns
    lines_with_votes = []
    for line in original_lines:
        line_text = line[0]  # Assuming the line structure is (text, vote_type)
        vote_type = None

        # Check for vote type using regex
        if aye_pattern.search(line_text):
            vote_type = 'Aye'
        elif nay_pattern.search(line_text):
            vote_type = 'Nay'
        elif abstain_pattern.search(line_text):
            vote_type = 'Abstain'
        else:
            vote_type = 'No Vote'  # Default if no patterns match

        lines_with_votes.append((line_text, vote_type))

    # Clear the breakdown box and prepare for categorized output
    breakdown_box.config(state=tk.NORMAL)
    breakdown_box.delete(1.0, tk.END)

    # Separate lines by vote type
    for vote_type in ['Aye', 'Nay', 'Abstain', 'No Vote']:
        # Filter lines by vote type
        filtered_lines = [line for line in lines_with_votes if line[1] == vote_type]

        if filtered_lines:
            # Insert a header for the vote type
            breakdown_box.insert(tk.END, f"{vote_type} Votes:\n")
            # Insert each line with its corresponding vote type
            for line_text, _ in filtered_lines:
                start_index = breakdown_box.index(tk.END)  # Get the current end index
                breakdown_box.insert(tk.END, line_text + "\n")  # Insert the line without tags
                # Highlight according to vote type
                end_index = breakdown_box.index(tk.END)  # Get the end index for the inserted line

            # Insert a separator line after the vote type
            breakdown_box.insert(tk.END, "-" * 80 + "\n")

    breakdown_box.config(state=tk.DISABLED)