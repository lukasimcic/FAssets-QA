from pathlib import Path
import json, os, re

from config.config_qa import secrets_folder


def secrets_file(num: int, partner: bool, funder: bool) -> Path:
    if funder:
        folder = secrets_folder
        file_name = "funder.json"
    else:
        folder = secrets_folder / f"user{'_partner' if partner else ''}"
        file_name = f"user{'_partner' if partner else ''}_{num}.json"
    return folder / file_name

def load_user_secrets(num: int, partner: bool, funder: bool = False) -> dict:
    file = secrets_file(num, partner, funder)
    with open(file) as f:
        return json.load(f)
    
def get_user_nums() -> list[int]:
    file_names = os.listdir(secrets_folder / "user")
    file_names = [f for f in file_names if re.match(r"user_\d+\.json", f)]
    return [int(re.search(r"user_(\d+)\.json", f).group(1)) for f in file_names]