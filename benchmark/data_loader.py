import json

class BaseDataLoader:
    def __init__(self):
        self.data = {}

    def load_from_json_string(self, json_str, name):
        self.data[name] = json.loads(json_str)

    def get_data(self, name):
        return self.data.get(name, [])

    def available_sets(self):
        return list(self.data.keys())
