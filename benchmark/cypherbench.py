import requests
import json

class CypherBenchLoader:
    HF_DATASET = "megagonlabs/cypherbench"
    CONFIG = "default"

    def __init__(self, split="train", offset=0, length=10000):
        self.split = split
        self.offset = offset
        self.length = length
        self.data = self.download_rows()

    def download_rows(self):
        url = (
            f"https://datasets-server.huggingface.co/rows?"
            f"dataset=megagonlabs%2Fcypherbench&config={self.CONFIG}&split={self.split}"
            f"&offset={self.offset}&length={self.length}"
        )
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error downloading rows: {response.status_code} - {response.text}")
        return response.json()

    def available_data(self):
        return self.data

    @staticmethod
    def list_splits():
        url = "https://datasets-server.huggingface.co/splits?dataset=megagonlabs%2Fcypherbench"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error listing splits: {response.status_code} - {response.text}")
        return response.json()

    @staticmethod
    def list_parquet_files(split="train"):
        url = f"https://huggingface.co/api/datasets/megagonlabs/cypherbench/parquet/{CypherBenchLoader.CONFIG}/{split}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error listing parquet files: {response.status_code} - {response.text}")
        return response.json()

if __name__ == "__main__":
    # Quick test: download 100 rows from the train split
    loader = CypherBenchLoader(split="train", offset=0, length=100)
    print("Number of rows downloaded:", len(loader.available_data().get("rows", [])))
    print("Available splits:")
    splits = CypherBenchLoader.list_splits()
    print(json.dumps(splits, indent=4, ensure_ascii=False))
    print("Parquet files for train split:")
    parquet = CypherBenchLoader.list_parquet_files(split="train")
    print(json.dumps(parquet, indent=4, ensure_ascii=False))
