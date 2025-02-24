import configparser

from google.oauth2.service_account import Credentials
from cryptography.fernet import Fernet
import json

#Loads the encrypted key for using the Google API from secret.key
def load_encrypted_json():
    config = configparser.ConfigParser()
    files_read = config.read('config/locationOfTxt.ini')
    keyLocation = config['key']['keyFile']
    autoupdateLocation = config['autoupdatejson']['autoupdatejsonFile']

    with open(keyLocation, "rb") as key_file:
        key = key_file.read()

    with open(autoupdateLocation, "rb") as enc_file:
        encrypted_data = enc_file.read()

    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()

    return json.loads(decrypted_data)