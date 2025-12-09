from pathlib import Path

# directory paths
config_folder = Path(__file__).resolve().parent
root_folder = config_folder.parent
fasset_bots_folder = root_folder / "fasset-bots"
contracts_folder = fasset_bots_folder / "packages" / "fasset-bots-core" / "artifacts" / "contracts"
secrets_folder = config_folder / "secrets"
data_folder = root_folder / "data"
log_folder = data_folder / "logs"

# contract names and addresses
coston2_contracts_file = config_folder / "contracts" / "coston2.json"
asset_manager_testxrp_instance_name = "AssetManager_FTestXRP"
asset_manager_controller_instance_name = "AssetManagerController"
fasset_testxrp_instance_name = "FTestXRP"
fdc_hub_instance_name = "FdcHub"
fdc_request_fee_configurations_instance_name = "FdcRequestFeeConfigurations"
relay_instance_name = "Relay"

# contract abi paths
asset_manager_path = contracts_folder / "assetManager" / "interfaces" / "IIAssetManager.sol" / "IIAssetManager.json"
fasset_path = contracts_folder / "fassetToken" / "interfaces" / "IIFAsset.sol" / "IIFAsset.json"
collateral_pool_path = contracts_folder / "collateralPool" / "interfaces" / "IICollateralPool.sol" / "IICollateralPool.json"
collateral_pool_token_path = contracts_folder / "collateralPool" / "implementation" / "CollateralPoolToken.sol" / "CollateralPoolToken.json"
fdc_hub_path = contracts_folder / "fdc" / "mock" / "FdcHubMock.sol" / "FdcHubMock.json"
fdc_request_fee_configurations_path = contracts_folder / "fdc" / "mock" / "FdcRequestFeeConfigurationsMock.sol" / "FdcRequestFeeConfigurationsMock.json"
relay_path = contracts_folder / "fdc" / "mock" / "RelayMock.sol" / "RelayMock.json"

# networks
tokens_native = ["C2FLR"]
tokens_underlying = ["testXRP"]
fasset_name = {
    "testXRP": "FTestXRP"
}
rpc_url = {
    "C2FLR": "https://coston2-api.flare.network/ext/C/rpc",
    "testXRP": "https://s.altnet.rippletest.net:51234/"
}
fdc_url = "https://testnet-verifier-fdc-test.aflabs.org"
da_url = "https://ctn2-data-availability.flare.network"
x_csrftoken = "dYBRCYd1bmuV5BfYrFctdMhh2obIameQ0zpWF7z8FE8ehAKVb9fjVckctfIqbZjp"

# hardcoded addresses
zero_address = "0x0000000000000000000000000000000000000000"
my_agent_vault = "0xbFF093BC39E082019964E6561F8b28ee2ed19303"
my_agent_pool = "0x07ac4CC44a4300E2aB33366771764B34d15C6FF5"
another_agent_vault = "0xd5889F2dF587332244AF3c29b7CAD0Dc4bA35Cd6"