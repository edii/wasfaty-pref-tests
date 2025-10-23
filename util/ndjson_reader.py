import json


class NdjsonReader:
    @staticmethod
    def read_records(filepath: str = ""):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line.strip())
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e} in file {filepath}")
            return

    @staticmethod
    def get_all_records(filepath: str = ""):
        return list(NdjsonReader.read_records(filepath))
