# Shared SQLite-backed access to the player roster, replacing the old per-tool
# players.txt loaders (VAplayerLoader, ACplayerLoader, CRplayerLoader).
import configparser
import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    name_lower    TEXT NOT NULL,
    position      TEXT NOT NULL,
    party         TEXT NOT NULL,
    riding        TEXT NOT NULL,
    start_date    TEXT NOT NULL,
    status        TEXT NOT NULL,
    is_vacant     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_players_name_lower ON players(name_lower);
"""


def _player_db_path():
    config = configparser.ConfigParser()
    config.read('config/locationOfTxt.ini')
    return config['playerdb']['playerDbFile']


def get_connection():
    return sqlite3.connect(_player_db_path())


def ensure_schema(conn=None):
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        if owns_conn:
            conn.close()


def _parse_players_lines(lines):
    """Canonical parser for the players.txt tab-separated format. Yields row tuples
    ready for INSERT, and a list of (line_number, raw_line) skipped as malformed."""
    rows = []
    skipped = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if line == "" or line.startswith(("Electoral District", "Party List")):
            continue

        parts = line.split('\t')
        if len(parts) < 6:
            skipped.append((line_number, line))
            continue

        name = parts[0].strip()
        position = parts[1].strip()
        party = parts[2].strip()
        riding = parts[3].strip()
        start_date = parts[4].strip()
        status = parts[5].strip() if parts[5].strip() else "Incumbent"
        is_vacant = 1 if name.lower() == "vacant" else 0

        rows.append((name, name.lower(), position, party, riding, start_date, status, is_vacant))

    return rows, skipped


def _replace_rows(conn, rows):
    conn.execute("DELETE FROM players")
    conn.executemany(
        "INSERT INTO players (name, name_lower, position, party, riding, start_date, status, is_vacant) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()


def import_from_txt(txt_path=None, conn=None, replace=True):
    """Import the players.txt interchange format into the DB. Returns (rows_imported, vacant_count)."""
    if txt_path is None:
        config = configparser.ConfigParser()
        config.read('config/locationOfTxt.ini')
        txt_path = config['player']['playerFile']

    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    return import_from_rows(lines, conn=conn, replace=replace)


def import_from_rows(rows, conn=None, replace=True):
    """Import already-in-memory tab-separated lines (e.g. from playerUpdater) into the DB.
    Returns (rows_imported, vacant_count)."""
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        ensure_schema(conn)
        parsed_rows, _skipped = _parse_players_lines(rows)
        if replace:
            _replace_rows(conn, parsed_rows)
        vacant_count = sum(1 for row in parsed_rows if row[7] == 1)
        return len(parsed_rows) - vacant_count, vacant_count
    finally:
        if owns_conn:
            conn.close()


def load_player_data():
    """VoteAnalyzer-compatible: {name_lower: [term_entry, ...]}, vacant_count."""
    conn = get_connection()
    try:
        ensure_schema(conn)
        player_data = {}
        vacant_count = 0
        cursor = conn.execute(
            "SELECT name_lower, position, party, riding, start_date, status, is_vacant FROM players"
        )
        for name_lower, position, party, riding, start_date, status, is_vacant in cursor:
            if is_vacant:
                vacant_count += 1
                continue
            entry = {
                "position": position,
                "party": party,
                "riding": riding,
                "date": start_date,
                "status": status,
            }
            player_data.setdefault(name_lower, []).append(entry)
        return player_data, vacant_count
    finally:
        conn.close()


def load_usernames_and_parties():
    """ActivityChecker-compatible: [(username, party), ...] for current incumbents."""
    conn = get_connection()
    try:
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT name, party FROM players WHERE is_vacant = 0 AND status = 'Incumbent'"
        )
        return [(name, party) for name, party in cursor]
    finally:
        conn.close()


def load_usernames():
    """CommentReader-compatible: [username, ...] (real reddit usernames, not position codes)."""
    conn = get_connection()
    try:
        ensure_schema(conn)
        cursor = conn.execute(
            "SELECT DISTINCT name FROM players WHERE is_vacant = 0"
        )
        return [name for (name,) in cursor]
    finally:
        conn.close()
