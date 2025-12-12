from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.attestation import Attestation
from config.config_qa import zero_address
from src.utils.data_storage_client import DataStorageClient
from src.utils.encoding import pad_0x, unpad_0x
from src.utils.data_structures import RedemptionStatus, UserData
from src.utils.fee_tracker import FeeTracker

class Redeemer(User):
    def __init__(self, user_data : UserData, fee_tracker : FeeTracker | None = None):
        super().__init__(user_data, fee_tracker)
        self.dsc = DataStorageClient(user_data, "redeem")

    def redeem(self, lots, executor=zero_address, executor_fee=0, log_steps=False):
        """
        Redeem underlying asset by calling the AssetManager contract.
        Saves redemption data for potential later default redemptions.
        Returns lots remaining to be redeemed if redemption request is incomplete.
        """
        self.log_step(f"Starting redemption of {lots} lots.", log_steps)
        am = AssetManager(self.token_native, self.token_underlying, self.native_data, self.fee_tracker)
        events = am.redeem(lots, self.underlying_data.address, executor, executor_fee)
        requested_redemptions, redemption_request_incomplete = events["RedemptionRequested"], events["RedemptionRequestIncomplete"]
        self.log_step(f"Redemption request submitted. Got {len(requested_redemptions)} requested redemptions.", log_steps)
        for requested_redemption in requested_redemptions:
            current_timestamp = NativeNetwork(self.token_native).get_current_timestamp()
            request_data = {
                "type" : "redeem",
                "requestId": str(requested_redemption.requestId),
                "amountUBA": str(requested_redemption.valueUBA - requested_redemption.feeUBA),
                "paymentReference": pad_0x(requested_redemption.paymentReference.hex()),
                "firstUnderlyingBlock": str(requested_redemption.firstUnderlyingBlock),
                "lastUnderlyingBlock": str(requested_redemption.lastUnderlyingBlock),
                "lastUnderlyingTimestamp": str(requested_redemption.lastUnderlyingTimestamp),
                "executorAddress": executor,
                "createdAt": self.dsc.timestamp_to_date(current_timestamp),
                "lots": lots
            } 
            self.dsc.save_record(request_data)
        return 0 if not redemption_request_incomplete else redemption_request_incomplete[0]["remainingLots"]
    
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
        a = Attestation(self.token_native, self.token_underlying, self.native_data, self.indexer_api_key, self.fee_tracker)
        request_body = a.request_body_referenced_payment_nonexistence(
            self.underlying_data.address,
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
        am = AssetManager(self.token_native, self.token_underlying, self.native_data, self.fee_tracker)
        am.redemption_payment_default(proof, redemption_id)
        self.log_step(f"Redemption default executed.", log_steps)
        self.dsc.remove_record(redemption_id)
        self.log_step(f"Redemption data removed from storage.", log_steps)

    def redemption_status(self):
        """
        Get statuses of all saved redemptions.
        """
        statuses = ["ACTIVE", "DEFAULTED_UNCONFIRMED", "SUCCESSFUL", "DEFAULTED_FAILED", "BLOCKED", "REJECTED"] # from RedemptionRequestInfo.sol
        result = {"pending": [], "default": [], "expired": [], "success": []}
        redemptions = self.dsc.get_records()
        am = AssetManager(self.token_native, self.token_underlying)
        for redemption in redemptions:
            redemption_id = int(redemption["requestId"])
            request_info = am.redemption_request_info(redemption_id)
            status = statuses[request_info[1]]
            if status == "ACTIVE":
                block = int(redemption["lastUnderlyingBlock"])
                current_underlying_block = UnderlyingNetwork(self.token_underlying).get_current_block()
                a = Attestation(self.token_native, self.token_underlying, self.native_data, self.indexer_api_key)
                first_block, _ = a.get_block_range()
                if current_underlying_block > block:
                    status = "default"
                elif block < first_block:
                    status = "expired"
                else:
                    status = "pending"
            elif status == "SUCCESSFUL":
                status = "success"
            else:
                status = "expired"
            result[status].append(redemption_id)
        return RedemptionStatus(**result)   

