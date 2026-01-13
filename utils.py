from datetime import datetime
from pathlib import Path
import json
from pprint import pprint

date = datetime.now().isoformat()
BASE_DIR = Path(__file__).resolve().parent


def isholiday(date: datetime):
    if date.weekday() > 5:
        return True
    else:
        return False


def read_json(json_file: Path):
    with open(json_file, "r") as file:
        data = json.loads(file.read())
        return data


if __name__ == "__main__":
    print(isholiday(date=datetime.fromisoformat(date)))
    data = read_json(Path(BASE_DIR, "calendar.json"))
    pprint(data)
