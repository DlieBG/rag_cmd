import requests
import zipfile
import io
from data_loader import BaseDataLoader

class SPCQLLoader(BaseDataLoader):
    ZIP_URL = "https://github.com/Guoaibo/Text-to-CQL/raw/main/dataset.zip"

    def __init__(self):
        super().__init__()
        self._load_data()

    def _load_data(self):
        response = requests.get(self.ZIP_URL)
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        for name in zip_file.namelist():
            if name.endswith(".json") and name.startswith("dataset/"):
                with zip_file.open(name) as f:
                    content = f.read().decode("utf-8")
                    short_name = name.split("/")[-1].replace(".json", "")
                    self.load_from_json_string(content, short_name)
