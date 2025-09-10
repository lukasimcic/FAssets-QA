from pathlib import Path
import json

# bot config
num_user_bots = 2
token_fasset = "FTestXRP"
token_underlying = "testXRP"
token_native = "C2FLR"
lot_size = 10

# directory paths
current_path = Path(__file__).resolve()  # the current file’s full path
root_path = current_path.parent.parent.parent
project_path = root_path / "fasset-bots"
log_path = root_path / "logs"
contract_path = project_path / "packages" / "fasset-bots-core" / "artifacts" / "contracts" / "userInterfaces"
asset_manager_path = contract_path / "IAssetManager.sol" / "IAssetManager.json"
coston2_qa_path = project_path / "test-data" / "coston2-qa.json"
secrets_files = [project_path / f"secrets-{i}.json" for i in range(num_user_bots)]

# contracts
rpc_url = "https://coston2-api.flare.network/ext/C/rpc"
with open(asset_manager_path, "r") as f:
    asset_manager_abi = json.load(f)["abi"]
with open(coston2_qa_path, "r") as f:
    coston2_contracts = json.load(f)
asset_manager_name = "AssetManager_FTestXRP"

# hardcoded addresses
my_agent_vault = "0xbFF093BC39E082019964E6561F8b28ee2ed19303"
my_agent_pool = "0x07ac4CC44a4300E2aB33366771764B34d15C6FF5"