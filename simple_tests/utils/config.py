from pathlib import Path

current_folder = Path(__file__).resolve()  # the current file’s full path
project_folder = current_folder.parent.parent.parent / "fasset-bots"

token_fasset = "FTestXRP"
token_underlying = "testXRP"
token_native = "C2FLR"
lot_size = 10
