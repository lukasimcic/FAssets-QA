from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.interfaces.network.native_networks.native_network import NativeNetwork
from src.interfaces.network.underlying_networks.underlying_network import UnderlyingNetwork
from src.interfaces.network.attestation import Attestation
from src.utils.data_storage import DataStorageClient
from src.utils.data_structures import MintStatus, UserData
from src.utils.fee_tracker import FeeTracker


class Minter(User):
    def __init__(self, user_data : UserData, fee_tracker : FeeTracker | None = None):
        super().__init__(user_data, fee_tracker)
        self.dsc = DataStorageClient(user_data, "mint")

    def _reserve_collateral(self, agent_vault, lots, executor):
        """
        Reserve collateral with the AssetManager contract.
        Returns paymentAddress, valueUBA, feeUBA, paymentReference.
        """
        am = AssetManager(self.token_native, self.token_underlying, self.native_data, self.fee_tracker)
        outputs = am.reserve_collateral(agent_vault, lots, executor)
        return outputs

    def _pay_underlying(self, payment_address, value_UBA, fee_UBA, payment_reference):
        """
        Pay underlying asset after reserving collateral.
        Returns dictionary including transaction hash, amount and fees paid.
        """
        un = UnderlyingNetwork(self.token_underlying, self.underlying_data, self.fee_tracker)
        amount = self.token_underlying.from_uba(value_UBA + fee_UBA)
        response = un.send_transaction(
            to_address=payment_address,
            amount=amount,
            memo_data=payment_reference.hex()
        )
        return response
    
    def _get_payment_proof(self, underlying_hash):
        a = Attestation(self.token_native, self.token_underlying, self.native_data, self.indexer_api_key, self.fee_tracker)
        request_body = a.request_body_payment(underlying_hash)
        response = a.prepare_attestation_request(request_body, "Payment")
        abi_encoded_request = response["abiEncodedRequest"]
        round_id = a.submit_attestation_request(abi_encoded_request)
        proof = a.get_proof(abi_encoded_request, round_id)
        return proof

    @staticmethod
    def _prepare_proof(proof):
        """
        Prepare the proof for contract submission.
        """
        response = proof['response']
        rqb = response['requestBody']
        request_body = (
            rqb['transactionId'],
            int(rqb['inUtxo']),
            int(rqb['utxo'])
        )
        rsb = response['responseBody']
        response_body = (
            int(rsb['blockNumber']),
            int(rsb['blockTimestamp']),
            rsb['sourceAddressHash'],
            rsb['sourceAddressesRoot'],
            rsb['receivingAddressHash'],
            rsb['intendedReceivingAddressHash'],
            int(rsb['spentAmount']),
            int(rsb['intendedSpentAmount']),
            int(rsb['receivedAmount']),
            int(rsb['intendedReceivedAmount']),
            rsb['standardPaymentReference'],
            bool(rsb['oneToOne']),
            int(rsb['status'])
        )
        proof_payment = (
            proof['proof'],
            (
                response['attestationType'],
                response['sourceId'],
                int(response['votingRound']),
                int(response['lowestUsedTimestamp']),
                request_body,
                response_body
            )
        )
        return proof_payment

    def _execute_minting(self, proof, collateral_reservation_id):
        """
        Execute minting after receiving attestation proof.
        """
        am = AssetManager(self.token_native, self.token_underlying, self.native_data, self.fee_tracker)
        tx = am.execute_minting(proof, collateral_reservation_id)
        return tx
    
    def _save_mint_request(self, reserve_collateral_data, tx_hash, lots):
        """
        Save mint request data to data storage.
        """
        current_timestamp = NativeNetwork(self.token_native).get_current_timestamp()
        request_data = {
            "type" : "mint",
            "requestId": str(reserve_collateral_data.collateralReservationId),
            "paymentAddress": reserve_collateral_data.paymentAddress,
            "transactionHash": tx_hash,
            "executorAddress": reserve_collateral_data.executor,
            "createdAt": self.dsc.timestamp_to_date(current_timestamp),
            "lots": lots
        }
        self.dsc.save_record(request_data)
    
    def mint(self, lots, agent_vault, executor="0x0000000000000000000000000000000000000000", log_steps=False):
        """
        Reserve collateral and pay underlying.
        Returns collateral reservation id.
        """
        self.log_step(f"Reserving {lots} lots at agent vault {agent_vault}...", log_steps)
        reserve_collateral_data = self._reserve_collateral(agent_vault, lots, executor)
        collateral_reservation_id = reserve_collateral_data.collateralReservationId
        self.log_step(f"Collateral reserved with id {collateral_reservation_id}.", log_steps)
        self.log_step(f"Paying underlying assets to {reserve_collateral_data.paymentAddress}...", log_steps)
        pay_underlying_outputs = self._pay_underlying(
            reserve_collateral_data.paymentAddress, 
            reserve_collateral_data.valueUBA, 
            reserve_collateral_data.feeUBA, 
            reserve_collateral_data.paymentReference
        )
        self.log_step(f"Paid {pay_underlying_outputs['amount']} {self.token_underlying}.", log_steps)
        self._save_mint_request(reserve_collateral_data, pay_underlying_outputs["tx_hash"], lots)
        return collateral_reservation_id

    def prove_and_execute_minting(self, collateral_reservation_id, log_steps=False):
        """
        Get attestation proof for the underlying payment and execute minting on AssetManager contract.
        """
        self.log_step(f"Retrieving mint request data for collateral reservation id {collateral_reservation_id}...", log_steps)
        mint_request = self.dsc.get_record(collateral_reservation_id)
        self.log_step("Getting payment proof...", log_steps)
        proof = self._get_payment_proof(mint_request["transactionHash"])
        self.log_step("Got payment proof.", log_steps)
        proof = self._prepare_proof(proof)
        self.log_step("Executing minting on AssetManager contract...", log_steps)
        tx = self._execute_minting(
            proof, 
            collateral_reservation_id
        )
        self.log_step(f"Minting executed in transaction: {tx.blockHash.hex()}.", log_steps)
        self.dsc.remove_record(collateral_reservation_id)

    def mint_status(self):
        """
        Returns the status of all mint requests in storage.
        """
        a = Attestation(self.token_native, self.token_underlying, self.native_data, self.indexer_api_key)
        first_block, _ = a.get_block_range()
        records = self.dsc.get_records()
        statuses = {"pending": [], "expired": []}
        for record in records:
            tx_hash = record["transactionHash"]
            request_id = int(record["requestId"])
            un = UnderlyingNetwork(self.token_underlying)
            tx_block = un.get_block_of_tx(tx_hash)
            if tx_block < first_block:
                statuses["expired"].append(request_id)
            else:
                statuses["pending"].append(request_id)
        return MintStatus(**statuses)

