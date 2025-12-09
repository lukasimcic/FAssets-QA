from config.config_qa import data_folder, asset_manager_controller_instance_name, fasset_name
from src.utils.contracts import get_contract_address
from src.utils.data_structures import UserData
from datetime import datetime, timezone
import json
import os


class DataStorageClient():
    def __init__(self, user_data : UserData, action_type):
        if action_type not in ["redeem", "mint"]:
            raise ValueError("action_type must be either 'redeem' or 'mint'")
        # set file name to match fasset-bots project format
        asset_manager_controller_snippet = get_contract_address(asset_manager_controller_instance_name)[2:10]
        user_name = f"user{'_partner' if user_data.partner else ''}_{user_data.num}"
        folder_name = f"{asset_manager_controller_snippet}-{fasset_name[user_data.token_underlying]}-{action_type}"
        self.folder = data_folder / "data_storage" / user_name[:-2] / user_name / folder_name
        if not self.folder.exists():
            os.makedirs(self.folder)

    @staticmethod
    def timestamp_to_date(timestamp):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def get_records(self):
        records = []
        for file_name in os.listdir(self.folder):
            if file_name.endswith(".json"):
                with open(self.folder / file_name, "r") as f:
                    records.append(json.load(f))
        return records
    
    def get_record(self, request_id):
        """
        Get redemption or mint data by its ID.
        """
        records = self.get_records()
        for record in records:
            if int(record["requestId"]) == request_id:
                return record
        raise ValueError(f"Request ID {request_id} not found.")

    def save_record(self, record_data):
        record_id = record_data.get("requestId")
        with open(self.folder / f"{record_id}.json", "w") as f:
            json.dump(record_data, f, indent=4)

    def remove_record(self, record_id):
        record_file = self.folder / f"{record_id}.json"
        if record_file.exists():
            os.remove(record_file)

    def add_data(self, record_id, data_dict):
        record = self.get_record(record_id)
        record.update(data_dict)
        self.save_record(record)

    def exists(self, record_id):
        record_file = self.folder / f"{record_id}.json"
        return record_file.exists()
    
    def get_existing_record_ids(self):
        existing_ids = [int(file_name.removesuffix(".json")) for file_name in os.listdir(self.folder) if file_name.endswith(".json")]
        return existing_ids
    
    def get_new_record_ids(self, previous_ids):
        existing_ids = [int(file_name.removesuffix(".json")) for file_name in os.listdir(self.folder) if file_name.endswith(".json")]
        return list(set(existing_ids).difference(set(previous_ids)))