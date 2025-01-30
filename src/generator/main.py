import yaml
from pathlib import Path

from json_query import PDDocumentQuery

def main():
    file_config = Path("config.yml")
    if file_config.exists():
        with open(file_config) as f:
            config = yaml.safe_load(f)
    else:
        print("Hij bestaat niet!")
    file_json = config["json"]
    document = PDDocumentQuery(file_json=file_json)


if __name__ == "__main__":
    main()