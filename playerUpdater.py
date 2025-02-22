# update_players.py
'''

DOCUMENTATION

 Program Purpose:
 	Allows the user to automatically update the players.txt file for use with the other applications within this grouping.
 	It takes the users from a spreadsheet and if there are any empty pieces of information it will go through the process of adapting it for further use.

'''
import gspread
from google.oauth2.service_account import Credentials
from cryptography.fernet import Fernet
import json

#Loads the encrypted key for using the google API from secret.key
def load_encrypted_json():
    with open("secret.key", "rb") as key_file:
        key = key_file.read()

    with open("autoupdater.json.enc", "rb") as enc_file:
        encrypted_data = enc_file.read()

    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()

    return json.loads(decrypted_data)

#Loads list of old players for votes which take place with a different set of MPs than the current
def load_old_players():
    try:
        with open('players.txt', 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

#Any removed players from players.txt are added to the oldplayer.txt file
def update_oldplayers_file(removed_players):
    with open('oldplayer.txt', 'a') as f:
        for player in removed_players:
            f.write(player + "\n")


def playerUpdater():
    creds_data = load_encrypted_json()
    creds = Credentials.from_service_account_info(creds_data, scopes=["https://www.googleapis.com/auth/spreadsheets",
                                                                      "https://www.googleapis.com/auth/drive"])

    client = gspread.authorize(creds)
    spreadsheet_key = "X"
    sheet = client.open_by_key(spreadsheet_key).worksheet("Voting Records")

    # Get all data from the specified columns, starting from row 6
    data = sheet.get_all_values()[3:]  # Start from row 6

    new_players = []
    seen = set()

    for row in data:
        if not row[1]:  # Stop if column B (row[0]) is empty
            break

        # Replace empty column G (row[6]) with "Incumbent" since row 6 is only filled if they have no end date on the spreadsheet
        row[6] = row[6] if row[6] else "Incumbent"
        entry = "\t".join(row[:7])  # Join columns B to G as a single entry

        if entry not in seen:  # Avoid duplicates
            new_players.append(entry)
            seen.add(entry)

    old_players = load_old_players()

    # Find removed players
    removed_players = set(old_players) - set(new_players)

    # Update players.txt with ordered new players
    with open('players.txt', 'w') as f:
        f.write("\n".join(new_players))

    # Update oldplayer.txt with removed players
    if removed_players:
        update_oldplayers_file(removed_players)

    print(f"players.txt has been updated! {len(removed_players)} players removed.")


if __name__ == "__main__":
    playerUpdater()
