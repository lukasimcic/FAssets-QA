from pathlib import Path

# bot config
NUM_USER_BOTS = 2

# directory paths
current_path = Path(__file__).resolve()  # the current file’s full path
root_path = current_path.parent.parent.parent
project_path = root_path / "fasset-bots"
log_path = root_path / "logs"
coston2_qa_path = project_path / "test-data" / "coston2-qa.json"
contracts_path = project_path / "packages" / "fasset-bots-core" / "artifacts" / "contracts"
user_secrets_files = [
    root_path / "secrets" / "user" / f"secrets-{i}.json" for i in range(NUM_USER_BOTS)
    ]
user_partner_secrets_files = [
    root_path / "secrets" / "user-partner" / f"secrets-{i}.json" for i in range(NUM_USER_BOTS)
    ]

# contract instance names
asset_manager_testxrp_instance_name = "AssetManager_FTestXRP"
fasset_testxrp_instance_name = "FTestXRP"
fdc_hub_instance_name = "FdcHub"
fdc_request_fee_configurations_instance_name = "FdcRequestFeeConfigurations"
relay_instance_name = "Relay"
# contract abi paths
asset_manager_path = contracts_path / "assetManager" / "interfaces" / "IIAssetManager.sol" / "IIAssetManager.json"
fasset_path = contracts_path / "fassetToken" / "interfaces" / "IIFAsset.sol" / "IIFAsset.json"
collateral_pool_path = contracts_path / "collateralPool" / "interfaces" / "IICollateralPool.sol" / "IICollateralPool.json"
collateral_pool_token_path = contracts_path / "collateralPool" / "interfaces" / "IICollateralPoolToken.sol" / "IICollateralPoolToken.json"
fdc_hub_path = contracts_path / "fdc" / "mock" / "FdcHubMock.sol" / "FdcHubMock.json"
fdc_request_fee_configurations_path = contracts_path / "fdc" / "mock" / "FdcRequestFeeConfigurationsMock.sol" / "FdcRequestFeeConfigurationsMock.json"
relay_path = contracts_path / "fdc" / "mock" / "RelayMock.sol" / "RelayMock.json"

# networks
rpc_url_c2flr = "https://coston2-api.flare.network/ext/C/rpc"
rpc_url_xrp = "https://s.altnet.rippletest.net:51234/"

# attestation
fdc_url = 'https://testnet-verifier-fdc-test.aflabs.org'
da_url = 'https://ctn2-data-availability.flare.network'
x_csrftoken = 'dYBRCYd1bmuV5BfYrFctdMhh2obIameQ0zpWF7z8FE8ehAKVb9fjVckctfIqbZjp'

# hardcoded addresses
zero_address = "0x0000000000000000000000000000000000000000"
my_agent_vault = "0xbFF093BC39E082019964E6561F8b28ee2ed19303"
my_agent_pool = "0x07ac4CC44a4300E2aB33366771764B34d15C6FF5"
another_agent_vault = "0xd5889F2dF587332244AF3c29b7CAD0Dc4bA35Cd6"