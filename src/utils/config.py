from pathlib import Path
import json

# bot config
num_user_bots = 1
token_fasset = "FTestXRP"
token_underlying = "testXRP"
token_native = "C2FLR"
lot_size = 10
decimals = 18

# directory paths
current_path = Path(__file__).resolve()  # the current file’s full path
root_path = current_path.parent.parent.parent
project_path = root_path / "fasset-bots"
log_path = root_path / "logs"
coston2_qa_path = project_path / "test-data" / "coston2-qa.json"
user_secrets_files = [
    project_path / "secrets" / "user" / f"secrets-{i}.json" for i in range(num_user_bots)
    ]
user_partner_secrets_files = [
    project_path / "secrets" / "user-partner" / f"secrets-{i}.json" for i in range(num_user_bots)
    ]

# contracts
rpc_url = "https://coston2-api.flare.network/ext/C/rpc"
asset_manager_instance_name = "AssetManager_FTestXRP"
contracts_path = project_path / "packages" / "fasset-bots-core" / "artifacts" / "contracts"
asset_manager_path = contracts_path / "assetManager" / "interfaces" / "IIAssetManager.sol" / "IIAssetManager.json"
collateral_pool_path = contracts_path / "collateralPool" / "interfaces" / "IICollateralPool.sol" / "IICollateralPool.json"
collateral_pool_token_path = contracts_path / "collateralPool" / "interfaces" / "IICollateralPoolToken.sol" / "IICollateralPoolToken.json"

# hardcoded addresses
my_agent_vault = "0xbFF093BC39E082019964E6561F8b28ee2ed19303"
my_agent_pool = "0x07ac4CC44a4300E2aB33366771764B34d15C6FF5"