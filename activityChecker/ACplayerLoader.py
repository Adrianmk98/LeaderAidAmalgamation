# Function to read usernames from names.txt and filter out "Vacant" and "Party List MP Party" lines
import configparser


def load_usernames_and_parties():
    users_and_parties = []
    config = configparser.ConfigParser()
    files_read = config.read('config/locationOfTxt.ini')
    PLAYER_DATA_FILE = config['player']['playerFile']
    with open(PLAYER_DATA_FILE, 'r') as file:
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