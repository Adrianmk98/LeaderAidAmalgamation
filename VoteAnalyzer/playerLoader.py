#Loads playerdata for the VoteAnalyzer from the path where the file is located
def load_player_data(playerFile):
    player_data = {}
    vacant_count = 0  # Initialize vacant count

    with open(playerFile, 'r') as file:
        for line in file:
            if line.strip() == "" or line.startswith(("Electoral District", "Party List")):
                continue

            parts = line.strip().split('\t')
            if len(parts) < 6:
                print(f"Skipping malformed line: {line.strip()}")
                continue

            name = parts[0].strip()
            position = parts[1].strip()  # Role (GOV, etc.)
            party = parts[2].strip()
            riding = parts[3].strip()
            date = parts[4].strip()
            status = parts[5].strip() if parts[5].strip() else "Incumbent"

            # Check if the name is "vacant"
            if name.lower() == 'vacant':
                vacant_count += 1
            else:
                # Create a new dictionary entry for this instance
                player_entry = {
                    "position": position,
                    "party": party,
                    "riding": riding,
                    "date": date,
                    "status": status
                }

                # Append to the list of entries for this name
                if name.lower() in player_data:
                    player_data[name.lower()].append(player_entry)
                else:
                    player_data[name.lower()] = [player_entry]

    return player_data, vacant_count