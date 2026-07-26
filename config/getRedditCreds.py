import configparser
import praw

REQUIRED_KEYS = ['client_id', 'client_secret', 'user_agent']


def _read_reddit_config():
    """Read config/config.ini and validate it has the required reddit keys.

    Returns the ConfigParser's 'reddit' section on success. Raises FileNotFoundError
    or ValueError on any problem, so callers that want a raw exception (fetch_reddit_creds)
    and callers that want a bool (setupCheck) can share the same validation logic.
    """
    config = configparser.ConfigParser()
    files_read = config.read('config/config.ini')
    if not files_read:
        raise FileNotFoundError("config.ini file not found. Please ensure it exists in the correct directory.")

    if 'reddit' not in config:
        raise ValueError("Missing 'reddit' section in config.ini")

    for key in REQUIRED_KEYS:
        if key not in config['reddit'] or not config['reddit'][key].strip():
            raise ValueError(f"Missing '{key}' in 'reddit' section of config.ini")

    return config['reddit']


def fetch_reddit_creds():
    try:
        reddit_section = _read_reddit_config()
        reddit = praw.Reddit(client_id=reddit_section['client_id'],
                              client_secret=reddit_section['client_secret'],
                              user_agent=reddit_section['user_agent'])
        return reddit

    except FileNotFoundError:
        raise FileNotFoundError("config.ini file not found. Please ensure it exists in the correct directory.")
    except ValueError as ve:
        raise ValueError(f"Configuration error: {ve}")
