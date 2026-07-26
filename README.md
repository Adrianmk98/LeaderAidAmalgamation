# CMHoC Vote Analyzer

A Windows desktop dashboard for moderating the Canadian Model House of Commons (CMHoC) subreddit. It
launches four independent Tkinter tools for working with Reddit threads and the member roster.

## Features

- **Vote Analyzer**: Analyze a Reddit thread's comments to tally Aye, Nay, and Abstain votes per MP,
  with sorting by vote type, party, or government position.
- **Activity Checker**: Check which MPs commented on qualifying debate threads within a date range.
- **Comment Reader**: Browse a thread's comments grouped by author, with unparliamentary-language and
  username highlighting, keybindable navigation, and read/unread tracking.
- **Player Updater**: Pull the current MP roster from a Google Sheet and rewrite `includes/players.txt`.

## Prerequisites

- Python 3.9+ (developed against 3.9.13)
- Reddit API credentials (script-type app)
- For the Player Updater tool only: a Google service-account key with access to the roster spreadsheet

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd CMHoCAppAmalgamation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

On Windows you can instead run `runmain.bat`, which checks for Python, installs
`requirements.txt`, and launches the app in one step.

### 3. Set up Reddit API credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" (or "Create Another App")
3. Set **App type** to "script", fill in a name, and use `http://localhost:8080` as the redirect URI
4. Note the **client_id** (under the app name) and **client_secret**
5. Fill in `config/config.ini`:
   ```ini
   [reddit]
   client_id = YOUR_CLIENT_ID
   client_secret = YOUR_CLIENT_SECRET
   user_agent = script:cmhocApp:v1.0 (by /u/YOUR_USERNAME)
   ```

`config/getRedditCreds.py` reads this file on every tool launch to build the `praw.Reddit` client used
throughout the app.

### 4. Configure data file locations

`config/locationOfTxt.ini` maps logical names to file paths and is read fresh by each loader:

```ini
[player]
playerFile=includes/players.txt
[oldplayer]
oldplayerFile=includes/oldplayer.txt
[unparliamentary]
unparliamentaryFile=includes/unparliamentary.txt
[votingsubreddit]
subreddit=none
[mainsubreddit]
mainreddit=none
[autoupdatejson]
autoupdatejsonFile=playerUpdater/autoupdater.json.enc
[key]
keyFile=playerUpdater/secret.key
```

The defaults already point at the files checked into `includes/` and `playerUpdater/`, so this only
needs editing if you relocate the data files.

### 5. Player roster format

`includes/players.txt` is tab-separated, one line per MP term, no header required:

```
Name	Position	Party	Riding	StartDate	Status
WonderOverYander	GOV	LPC	Fraser-Columbia and the North	30/12/2024	Incumbent
```

- **Name**: Reddit username (matched case-insensitively)
- **Position**: e.g. `GOV`, `OPP`, `MP`
- **Party**: party abbreviation (`LPC`, `CPC`, `NDP`, `FMR`, ...)
- **Riding**: electoral district name
- **StartDate**: `DD/MM/YYYY` (falls back to `MM/DD/YYYY` if that fails to parse)
- **Status**: `Incumbent`, or an end date in the same format
- A name of `vacant` is counted separately and excluded from the loaded roster
- A person can appear on multiple rows if they've held more than one term; the Vote Analyzer picks
  whichever row covers the date of the thread being analyzed

This file can be maintained by hand or regenerated via the Player Updater tool (see below).

## Usage

### Starting the application

```bash
python Main.py
```

Run this from the repo root — every tool resolves config, data, and logo files with paths relative to
the current working directory. This opens the dashboard with four buttons, one per tool.

### Vote Analyzer

1. Open Vote Analyzer from the dashboard.
2. Paste a Reddit thread URL (or use "Open Recent Posts" to browse the last 1–30 days of posts in
   `r/cmhocvote`), then click "Analyze Votes".
3. Review the per-member breakdown and the tally, and re-sort by vote type, party, or government
   position with the buttons on the right.

Vote keywords are matched with fuzzy regex, tolerating 1–3 character typos:
- **Aye**: aye, oui, yea, pour
- **Nay**: nay, non, contre
- **Abstain**: abstain, abstention

### Activity Checker

1. Open Activity Checker from the dashboard.
2. Pick a start and end date and click "Check Comments".
3. It scans `r/cmhoc` for posts with a qualifying debate flair (Question Period, 2nd/3rd Reading,
   Committee of the Whole, Motion Debate, Report Stage, Take-Note Debate, Motion Amendments) in that
   window, and reports which currently-incumbent MPs commented.
4. Select a name in the results list to see links to their individual comments.

### Comment Reader

1. Open Comment Reader from the dashboard, paste a thread URL, and press Enter (or click "Fetch
   Comments").
2. Pick an author from the dropdown to see their comments in that thread; usernames and
   unparliamentary-language matches (from `includes/unparliamentary.txt`) are highlighted.
3. Mark comments as read, open them in the browser, or jump between users/comments with the
   configurable keybindings (see the Help menu).

### Player Updater

1. Open Player Updater from the dashboard.
2. It decrypts the Google service-account credentials in `playerUpdater/autoupdater.json.enc` (using
   `playerUpdater/secret.key`) and pulls the "Voting Records" worksheet from the configured Google
   Sheet, then rewrites `includes/players.txt` and appends any removed members to
   `includes/oldplayer.txt`.

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt --upgrade
```

**Reddit authentication fails**
- Verify `config/config.ini` has valid `client_id`, `client_secret`, and `user_agent`
- Confirm the Reddit app is registered as "script" type

**Player data not loading**
- Verify `playerFile` in `config/locationOfTxt.ini` points at the right path
- Confirm `includes/players.txt` uses tab-separated values with dates in `DD/MM/YYYY` format

**Logo images missing**
- Ensure `logos/logored.png`, `logos/logoblue.png`, and `logos/logoorange.png` exist relative to the
  working directory you launched `python Main.py` from

### Error logs

The app prints debug information to stdout — run it from a terminal (or `runmain.bat`, which keeps the
console window open) to see error and parsing messages.

## Security note

`config/config.ini`, `playerUpdater/secret.key`, and `playerUpdater/autoupdater.json.enc` in this repo
contain live credentials rather than placeholders. Treat this repository as private, and rotate those
credentials if it's ever made public.
