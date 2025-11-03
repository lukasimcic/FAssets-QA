from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.interfaces.network.network import Network
from src.interfaces.network.attestation import Attestation
from config.config_qa import zero_address
from src.utils.data_storage_client import DataStorageClient
from src.utils.encoding import pad_0x, unpad_0x

class Redeemer(User):
    def __init__(self, token_native, token_underlying, num=0, partner=False, config=None):
        super().__init__(token_underlying, num, partner)
        self.token_underlying = token_underlying
        self.nn = Network(token_native, self.native_data["address"], self.native_data["private_key"])
        self.num = num
        self.partner = partner
        self.native_address = self.native_data["address"]
        self.native_private_key = self.native_data["private_key"]
        self.underlying_public_key = self.underlying_data["public_key"]
        self.underlying_private_key = self.underlying_data["private_key"]
        self.underlying_address = self.underlying_data["address"]
        self.dsc = DataStorageClient(num, partner, token_underlying, "redeem")
        # TODO add support for custom config
        if config is not None:
            raise NotImplementedError("Custom config is not yet supported.")

    def redeem(self, lots, executor=zero_address, executor_fee=0, log_steps=False):
        """
        Redeem underlying asset by calling the AssetManager contract.
        Saves redemption data for potential later default redemptions.
        Returns lots remaining to be redeemed if redemption request is incomplete.
        """
        self.log_step(f"Starting redemption of {lots} lots.", log_steps)
        am = AssetManager(self.native_address, self.native_private_key, self.token_underlying)
        requested_redemptions, redemption_request_incomplete = am.redeem(lots, self.underlying_address, executor, executor_fee)
        self.log_step(f"Redemption request submitted. Got {len(requested_redemptions)} requested redemptions.", log_steps)
        for requested_redemption in requested_redemptions:
            current_timestamp = self.nn.get_current_timestamp()
            request_data = {
                "type" : "redeem",
                "requestId": str(requested_redemption.requestId),
                "amountUBA": str(requested_redemption.valueUBA - requested_redemption.feeUBA),
                "paymentReference": pad_0x(requested_redemption.paymentReference.hex()),
                "firstUnderlyingBlock": str(requested_redemption.firstUnderlyingBlock),
                "lastUnderlyingBlock": str(requested_redemption.lastUnderlyingBlock),
                "lastUnderlyingTimestamp": str(requested_redemption.lastUnderlyingTimestamp),
                "executorAddress": executor,
                "createdAt": self.dsc.timestamp_to_date(current_timestamp)
            }
            self.dsc.save_record(request_data)
        return redemption_request_incomplete[0]["remaining_lots"] if redemption_request_incomplete else 0
    
    def _prepare_proof(self, proof):
        """
        Format the attestation proof response for redemptionPaymentDefault contract call.
        """
        response = proof['response']
        rqb = response['requestBody']
        rsb = response['responseBody']
        merkle_proof = proof['proof']  
        contract_proof = (
            merkle_proof,
            (
                response['attestationType'], 
                response['sourceId'],        
                int(response['votingRound']),
                int(response['lowestUsedTimestamp']),
                (
                    int(rqb['minimalBlockNumber']),
                    int(rqb['deadlineBlockNumber']),
                    int(rqb['deadlineTimestamp']),
                    rqb['destinationAddressHash'],
                    int(rqb['amount']),
                    rqb['standardPaymentReference'],
                    bool(rqb['checkSourceAddresses']),
                    rqb['sourceAddressesRoot'],
                ),
                (
                    int(rsb['minimalBlockTimestamp']),
                    int(rsb['firstOverflowBlockNumber']),
                    int(rsb['firstOverflowBlockTimestamp']),
                )
            )
        )
        return contract_proof

    def _get_referenced_payment_non_existence_proof(self, redemption_data):
        """
        Get attestation proof for referenced payment non-existence.
        """
        a = Attestation("testXRP", self.native_data, self.underlying_data, self.indexer_api_key)
        request_body = a.request_body_referenced_payment_nonexistence(
            self.underlying_data["address"],
            unpad_0x(redemption_data["paymentReference"]),
            redemption_data["amountUBA"],
            redemption_data["firstUnderlyingBlock"],
            redemption_data["lastUnderlyingBlock"],
            redemption_data["lastUnderlyingTimestamp"]
        )
        response = a.prepare_attestation_request(request_body, "ReferencedPaymentNonexistence")
        abi_encoded_request = response["abiEncodedRequest"]
        round_id = a.submit_attestation_request(abi_encoded_request)
        proof = a.get_proof(abi_encoded_request, round_id)
        return proof

    def redeem_default(self, redemption_id, log_steps=False):
        """
        Redeem a default redemption by its ID.
        """
        self.log_step(f"Starting default redemption for ID {redemption_id}.", log_steps)
        redemption_data = self.dsc.get_record(redemption_id)
        self.log_step("Getting referenced payment non existence proof ...", log_steps)
        proof = self._get_referenced_payment_non_existence_proof(redemption_data)
        proof = self._prepare_proof(proof)
        self.log_step("Got proof.", log_steps)
        redemption_id = int(redemption_data["requestId"])
        self.log_step(f"Submitting redemption default payment.", log_steps)
        am = AssetManager(self.native_data["address"], self.native_data["private_key"], self.token_underlying)
        am.redemption_payment_default(proof, redemption_id)
        self.log_step(f"Redemption default executed.", log_steps)
        self.dsc.remove_record(redemption_id)
        self.log_step(f"Redemption data removed from storage.", log_steps)

    def redemption_status(self):
        """
        Get statuses of all saved redemptions.
        """
        statuses = ["ACTIVE", "DEFAULTED_UNCONFIRMED", "SUCCESSFUL", "DEFAULTED_FAILED", "BLOCKED", "REJECTED"] # from RedemptionRequestInfo.sol
        result = {"PENDING": [], "DEFAULT": [], "EXPIRED": [], "SUCCESS": []}
        redemptions = self.dsc.get_records()
        am = AssetManager("","", self.token_underlying)
        for redemption in redemptions:
            redemption_id = int(redemption["requestId"])
            request_info = am.redemption_request_info(redemption_id)
            status = statuses[request_info[1]]
            if status == "ACTIVE":
                block = int(redemption["lastUnderlyingBlock"])
                current_underlying_block = Network(self.token_underlying, "", "").get_current_block()
                a = Attestation("testXRP", self.native_data, self.underlying_data, self.indexer_api_key)
                first_block, _ = a.get_block_range()
                if current_underlying_block > block:
                    status = "DEFAULT"
                elif block < first_block:
                    status = "EXPIRED"
                else:
                    status = "PENDING"
            elif status == "SUCCESSFUL":
                status = "SUCCESS"
            else:
                status = "EXPIRED"
            result[status].append(redemption_id)
        return result

