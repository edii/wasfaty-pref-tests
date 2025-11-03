import random
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path


def random_list(data: List[Dict]):
    return random.choice(data)

def random_birth_date(ages: dict, gender: str) -> (datetime, int):
    age_numbers = list(ages.keys())
    weights = []
    for item in ages.values():
        weights.append(item[gender])

    age_year = random.choices(age_numbers, weights)[0]

    now = datetime.today()
    year_of_birth = now - timedelta(days=age_year * 365)
    date_of_birth = year_of_birth + timedelta(days=(random.randrange(-365, 365)))
    if date_of_birth > now:
        date_of_birth = now

    return (date_of_birth.date(), age_year)

def random_randrange(start: int, stop: int) -> int:
    return random.randrange(start, stop)


def mkdir(dir: str):
    directory_path = Path(dir)
    directory_path.mkdir(parents=True, exist_ok=True)
    print(f"Directory '{directory_path}' ensured to exist.")
