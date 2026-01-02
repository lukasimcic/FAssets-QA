from config.config_qa import secrets_folder
import json, os, re

def secrets_file(num, partner, funder):
    if funder:
        folder = secrets_folder
        file_name = "funder.json"
    else:
        folder = secrets_folder / f"user{'_partner' if partner else ''}"
        file_name = f"user{'_partner' if partner else ''}_{num}.json"
    return folder / file_name

def load_user_secrets(num, partner, funder=False):
    file = secrets_file(num, partner, funder)
    with open(file) as f:
        return json.load(f)
    
def get_user_nums():
    file_names = os.listdir(secrets_folder / "user")
    file_names = [f for f in file_names if re.match(r"user_\d+\.json", f)]
    return [int(re.search(r"user_(\d+)\.json", f).group(1)) for f in file_names]