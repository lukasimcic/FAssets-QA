from src.interfaces.user.user import User
from src.interfaces.contracts import *
from src.interfaces.networks.network import Network
from src.interfaces.networks.attestation import Attestation


class Minter(User):
    def __init__(self, token_underlying, num=0, partner=False, config=None):
        super().__init__(token_underlying, num, partner)
        self.token_underlying = token_underlying
        self.native_address = self.native_data["address"]
        self.native_private_key = self.native_data["private_key"]
        self.underlying_public_key = self.underlying_data["public_key"]
        self.underlying_private_key = self.underlying_data["private_key"]
        # TODO add support for custom config
        if config is not None:
            raise NotImplementedError("Custom config is not yet supported.")

    def _reserve_collateral(self, agent_vault, lots, executor):
        """
        Reserve collateral with the AssetManager contract.
        Returns paymentAddress, valueUBA, feeUBA, paymentReference.
        """
        am = AssetManager(self.native_address, self.native_private_key, self.token_underlying)
        outputs = am.reserve_collateral(agent_vault, lots, executor)
        return outputs
    
    def _pay_underlying(self, payment_address, value_UBA, fee_UBA, payment_reference):
        """
        Pay underlying asset after reserving collateral.
        """
        un = Network(
            token=self.token_underlying,
            public_key=self.underlying_public_key, 
            private_key=self.underlying_private_key
            )
        amount = (value_UBA + fee_UBA) / un.asset_unit_uba
        response = un.send_transaction(
            to_address=payment_address,
            amount=amount,
            memo_data=payment_reference.hex()
        )
        return response.result["tx_json"]["hash"], amount
    
    def _get_attestation_proof(self, underlying_hash):
        a = Attestation("testXRP", self.native_data, self.underlying_data, self.indexer_api_key)
        response = a.prepare_attestation_request(underlying_hash, "Payment")
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
        am = AssetManager(self.native_address, self.native_private_key, self.token_underlying)
        tx = am.execute_minting(proof, collateral_reservation_id)
        return tx
    
    def mint(self, lots, agent_vault, executor="0x0000000000000000000000000000000000000000", log_steps=False):
        """
        Complete minting process: reserve collateral, pay underlying, get attestation proof, and execute minting.
        """
        self.log_step(f"Reserving {lots} lots at agent vault {agent_vault}...", log_steps)
        reserve_collateral_data = self._reserve_collateral(agent_vault, lots, executor)
        collateral_reservation_id = reserve_collateral_data.collateralReservationId
        self.log_step(f"Collateral reserved with id {collateral_reservation_id}.", log_steps)
        self.log_step(f"Paying underlying assets to {reserve_collateral_data.paymentAddress}...", log_steps)
        tx_hash, amount = self._pay_underlying(
            reserve_collateral_data.paymentAddress, 
            reserve_collateral_data.valueUBA, 
            reserve_collateral_data.feeUBA, 
            reserve_collateral_data.paymentReference
        )
        self.log_step(f"Paid {amount} {self.token_underlying}.", log_steps)
        self.log_step("Getting attestation proof...", log_steps)
        proof = self._get_attestation_proof(tx_hash)
        self.log_step("Got attestation proof.", log_steps)
        proof = self._prepare_proof(proof)
        self.log_step("Executing minting on AssetManager contract...", log_steps)
        tx = self._execute_minting(
            proof, 
            collateral_reservation_id
        )
        self.log_step("Minting executed.", log_steps)

