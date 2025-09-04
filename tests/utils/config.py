from pathlib import Path
import json

current_folder = Path(__file__).resolve()  # the current file’s full path
root_folder = current_folder.parent.parent.parent
project_folder = root_folder / "fasset-bots"
log_folder = root_folder / "logs"

num_user_bots = 2
secrets_files = [project_folder / f"secrets-{i}.json" for i in range(num_user_bots)]

token_fasset = "FTestXRP"
token_underlying = "testXRP"
token_native = "C2FLR"
lot_size = 10