# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Windows desktop Tkinter application (no packaging as a Python package — plain scripts run from the
repo root) for the Canadian Model House of Commons (CMHoC) subreddit moderation team. `Main.py` is a
dashboard that launches one of four independent Tkinter tools, each in its own subpackage:

- `VoteAnalyzer/` — fetches a Reddit post/thread and tallies Aye/Nay/Abstain votes from comments.
- `activityChecker/` — scans a subreddit over a date range for MPs' comment activity on specific flairs.
- `commentReader/` — lets a moderator page through a thread's comments grouped by author.
- `playerUpdater/` — pulls the roster from a Google Sheet and rewrites `includes/players.txt`.

## Commands

```bash
pip install -r requirements.txt   # install dependencies
python Main.py                    # launch the dashboard (run from repo root — file paths are relative)
```

`runmain.bat` does the same on a fresh Windows machine (checks for Python, installs
`requirements.txt`, then runs `Main.py`). There is no test suite, linter, or build script configured;
`build/` contains stale PyInstaller output from a previous packaging attempt, not a build you should
regenerate unless asked.

## Architecture

**Entry point pattern**: `Main.py` creates a hidden root `tk.Tk()` and each tool's `main()` creates its
own `tk.Toplevel()` on a *second* hidden root — every tool module (`voteanalyzerMain.py`,
`activitycheckMain.py`, `commentreaderMain.py`) does `rootx = tk.Tk(); rootx.withdraw(); root =
tk.Toplevel()` rather than accepting the dashboard's root as a parameter. Each tool can therefore also
be run standalone via its own `if __name__ == "__main__"` block.

**State is module-level globals, not classes**: every GUI module declares its Tkinter widgets as
`global` inside `main()` (e.g. `entry_link`, `breakdown_box`, `reddit`) and other functions in the same
file reach into those globals directly. There are no widget classes. When editing one of these modules,
follow the existing pattern rather than introducing OO structure — a partial refactor will break the
sibling functions that still expect the globals.

**Config resolution — two separate ini files, read fresh on every call**:
- `config/config.ini` — Reddit API credentials (`client_id`, `client_secret`, `user_agent`), consumed
  once by `config/getRedditCreds.py:fetch_reddit_creds()` to build a `praw.Reddit` instance. Every tool
  calls this itself in its own `main()`; there is no shared/cached Reddit client.
- `config/locationOfTxt.ini` — indirection layer mapping logical names to file paths (`playerFile`,
  `oldplayerFile`, `unparliamentaryFile`, `autoupdatejsonFile`, `keyFile`), plus `votingsubreddit` /
  `mainsubreddit` keys that are currently unused (set to `none`). Loaders
  (`VAplayerLoader.load_player_data`, `ACplayerLoader.load_usernames_and_parties`,
  `CRplayerLoader.load_usernames`) each re-read this ini and re-parse the player file independently —
  there's no shared cache, so a large roster file gets parsed once per widget action, not once per
  session. `commentreaderMain.py` also reads `includes/players.txt` and `includes/unparliamentary.txt`
  directly by hardcoded path instead of going through `locationOfTxt.ini`.

Both ini files, and all paths inside `includes/`/`playerUpdater/`, are relative to the process's current
working directory — every script assumes it's launched from the repo root (as `Main.py` and
`runmain.bat` do).

**Player roster format** (`includes/players.txt`, tab-separated, no header required):
```
Name<TAB>Position<TAB>Party<TAB>Riding<TAB>StartDate(DD/MM/YYYY)<TAB>Status
```
`Status` is either `Incumbent` or an end date in the same format. A name of `vacant` (case-insensitive)
is counted but excluded from the loaded roster. Names are looked up case-insensitively against Reddit
usernames. A person can have multiple rows (one per term); vote/eligibility logic in
`voteanalyzerMain.analyze_votes` picks whichever row's date range covers the submission's timestamp.

**Vote detection**: `VoteAnalyzer/voteanalyzerMain.py` uses fuzzy regex (`regex` module, not stdlib `re`)
with an edit-distance tolerance (`{e<=1}`, `{e<=3}`) to match Aye/Nay/Abstain keywords in French and
English against each eligible MP's most recent comment on the thread, converting the submission
timestamp from UTC to America/New_York to determine which roster entries were valid at vote time.
`sortingData.py` re-sorts the already-rendered `breakdown_box` Text widget by re-parsing its own
inserted text (via bracket/position string-slicing) rather than resorting the original vote data
structure — the display and the data model are the same string.

**playerUpdater is a separate credential domain**: `playerUpdater.py` / `loadEncrypedCode.py` don't use
`config/config.ini` at all. They decrypt `playerUpdater/autoupdater.json.enc` (a Google service-account
key) using the Fernet key in `playerUpdater/secret.key` (path from `locationOfTxt.ini`'s `[key]`
section), then use `gspread` to pull the "Voting Records" worksheet (hardcoded spreadsheet key,
currently a placeholder `"X"`) and rewrite `includes/players.txt`. Note
`load_old_players()` reads from `includes/playerFiles/players.txt`, a path that doesn't exist anywhere
else in the repo (likely dead/broken code — `includes/oldplayer.txt` is the file actually read
elsewhere via `locationOfTxt.ini`'s `oldplayerFile` key, which itself points at a filename,
`oldplayers.txt`, that also doesn't match the file on disk, `oldplayer.txt`).

## Known gotchas when modifying this code

- **Secrets are committed to this repo**: `config/config.ini` (Reddit client secret),
  `playerUpdater/secret.key`, and `playerUpdater/autoupdater.json.enc` all contain real credentials
  checked into git, not templates. Don't add new secrets the same way — flag it if asked to touch these
  files.
- No `__init__.py` files exist; the subpackages import each other via absolute imports (e.g. `from
  VoteAnalyzer.sortingData import ...`) that only resolve because Python 3 implicit namespace packages
  make every directory importable, combined with the repo root being on `sys.path` when run as `python
  Main.py`. Don't assume `pip install -e .`-style installability.
- Logo assets are loaded with hardcoded relative paths (`logos/logored.png`, etc.) — another reason
  every entry point must be launched from the repo root.
- `activitycheckMain.py` and `voteanalyzerMain.py`/`commentreaderMain.py` each independently call
  `fetch_reddit_creds()`, so opening multiple tools from the dashboard authenticates with Reddit
  multiple times in the same session.
