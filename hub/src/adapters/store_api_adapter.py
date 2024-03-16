import json
import logging
from typing import List

import requests

from src.entities.processed_agent_data import ProcessedAgentData
from src.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch: Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        try:
            json_str = "["
            for data in processed_agent_data_batch:
                json_str = json_str + data.model_dump_json() + ","
            json_str = json_str[:-1] + "]"
            response = requests.post(
                f"{self.api_base_url}/processed_agent_data/",
                json=json.loads(json_str),
            )
            # json_data = [data.model_dump_json() for data in processed_agent_data_batch]
            # response = requests.post(
            #     f"{self.api_base_url}/processed_agent_data/",
            #     json=json_data,
            # )
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Error saving data to Store API: {e}")
            return False
