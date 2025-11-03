from config.config_qa import secrets_folder
import json

def secrets_file(num, partner):
    folder = secrets_folder / f"user{'_partner' if partner else ''}"
    file_name = f"user{'_partner' if partner else ''}_{num}.json"
    return folder / file_name

def load_user_secrets(num, partner):
    file = secrets_file(num, partner)
    with open(file) as f:
        return json.load(f)