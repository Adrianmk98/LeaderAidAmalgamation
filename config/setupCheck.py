import configparser
import os
import sqlite3

from config.getRedditCreds import _read_reddit_config


def has_valid_reddit_config():
    try:
        _read_reddit_config()
        return True
    except (FileNotFoundError, ValueError):
        return False


def _player_db_path():
    config = configparser.ConfigParser()
    config.read('config/locationOfTxt.ini')
    return config['playerdb']['playerDbFile']


def has_player_db():
    db_path = _player_db_path()
    if not os.path.exists(db_path):
        return False

    try:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
            return cursor.fetchone() is not None
        finally:
            conn.close()
    except sqlite3.Error:
        return False
