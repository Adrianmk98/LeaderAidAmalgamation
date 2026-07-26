# update_players.py
'''

DOCUMENTATION

 Program Purpose:
 	Allows the user to automatically update the players.txt file for use with the other applications within this grouping.
 	It takes the users from a spreadsheet and if there are any empty pieces of information it will go through the process of adapting it for further use.

'''
import configparser

import gspread
from google.oauth2.service_account import Credentials
from cryptography.fernet import Fernet
import json

from playerUpdater.loadEncrypedCode import load_encrypted_json
from includes.playerDB import import_from_rows


def _location_config():
    config = configparser.ConfigParser()
    config.read('config/locationOfTxt.ini')
    return config


#Loads list of old players for votes which take place with a different set of MPs than the current
#Reads the *current* players.txt, before this run overwrites it, so removed players can be diffed
def load_old_players():
    player_file = _location_config()['player']['playerFile']
    try:
        with open(player_file, 'r') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

#Any removed players from players.txt are added to the oldplayer.txt file
def update_oldplayers_file(removed_players):
    oldplayer_file = _location_config()['oldplayer']['oldplayerFile']
    with open(oldplayer_file, 'a') as f:
        for player in removed_players:
            f.write(player + "\n")


def playerUpdater(log=print):
    log("Decrypting Google service-account credentials...")
    creds_data = load_encrypted_json()
    creds = Credentials.from_service_account_info(creds_data, scopes=["https://www.googleapis.com/auth/spreadsheets",
                                                                      "https://www.googleapis.com/auth/drive"])

    log("Authorizing with Google Sheets...")
    client = gspread.authorize(creds)
    spreadsheet_key = "X"
    sheet = client.open_by_key(spreadsheet_key).worksheet("Voting Records")

    log("Fetching \"Voting Records\" worksheet...")
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
    player_file = _location_config()['player']['playerFile']
    with open(player_file, 'w') as f:
        f.write("\n".join(new_players))

    # Rebuild players.db from the same in-memory rows, so txt and DB never disagree
    log("Rebuilding player database...")
    import_from_rows(new_players)

    # Update oldplayer.txt with removed players
    if removed_players:
        update_oldplayers_file(removed_players)

    log(f"players.txt has been updated! {len(new_players)} players written, {len(removed_players)} removed.")


if __name__ == "__main__":
    playerUpdater()
