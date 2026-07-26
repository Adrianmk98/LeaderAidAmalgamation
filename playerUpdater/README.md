# Player Updater

Pulls the MP roster from a Google Sheet and rewrites `includes/players.txt` and
`includes/players.db`. This tool is optional -- every other tool in this app works fine without it,
as long as `includes/players.txt` already has roster data in it.

## Required files (not checked into git)

- `playerUpdater/secret.key` -- a Fernet key.
- `playerUpdater/autoupdater.json.enc` -- a Google service-account JSON key, encrypted with that
  Fernet key.

To generate these from scratch:

1. Create a Google Cloud service account with access to the target spreadsheet, and download its
   JSON key file.
2. Generate a Fernet key and save it as `playerUpdater/secret.key`:
   ```python
   from cryptography.fernet import Fernet
   open('playerUpdater/secret.key', 'wb').write(Fernet.generate_key())
   ```
3. Encrypt the downloaded service-account JSON with that key and save it as
   `playerUpdater/autoupdater.json.enc`:
   ```python
   from cryptography.fernet import Fernet
   key = open('playerUpdater/secret.key', 'rb').read()
   data = open('path/to/service-account.json', 'rb').read()
   open('playerUpdater/autoupdater.json.enc', 'wb').write(Fernet(key).encrypt(data))
   ```

## Spreadsheet key

`playerUpdater/playerUpdater.py` has a placeholder `spreadsheet_key = "X"` -- replace it with the
real Google Sheet key for the "Voting Records" spreadsheet before running a sync, or the sync will
fail.
