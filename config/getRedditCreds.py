import configparser
import praw
def fetch_reddit_creds():
    config = configparser.ConfigParser()

    # Try to read the config file and handle errors if it doesn't exist or is improperly formatted
    try:
        files_read = config.read('config/config.ini')
        if 'reddit' not in config:
            raise ValueError("Missing 'reddit' section in config.ini")

        # Ensure all necessary keys exist in the 'reddit' section
        required_keys = ['client_id', 'client_secret', 'user_agent']
        for key in required_keys:
            if key not in config['reddit']:
                raise ValueError(f"Missing '{key}' in 'reddit' section of config.ini")

        reddit=praw.Reddit(client_id=config['reddit']['client_id'],
                           client_secret=config['reddit']['client_secret'],
                           user_agent=config['reddit']['user_agent'])
        return reddit

    except FileNotFoundError:
        raise FileNotFoundError("config.ini file not found. Please ensure it exists in the correct directory.")
    except ValueError as ve:
        raise ValueError(f"Configuration error: {ve}")