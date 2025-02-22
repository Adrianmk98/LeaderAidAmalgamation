# Function to read usernames from names.txt and filter out "Vacant" and "Party List MP Party" lines
import configparser
def load_usernames():
    users = []
    config = configparser.ConfigParser()
    files_read = config.read('config/locationOfTxt.ini')
    PLAYER_DATA_FILE = config['player']['playerFile']
    with open(PLAYER_DATA_FILE, 'r', encoding='utf-8') as file:
        for line in file:
            # Strip any leading or trailing spaces
            clean_line = line.strip()

            # Skip empty lines, lines with "vacant", and lines starting with "Party List"
            if clean_line == "" or "vacant" in clean_line.lower() or clean_line.startswith("Party List"):
                continue

            # Split the line by tab to extract the relevant fields
            parts = clean_line.split('\t')
            if len(parts) >= 3 and parts[1].lower() != "vacant":
                username = parts[1]  # Extract the name (second item)
                users.append(username)

    return users