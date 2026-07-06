import random


def generate_confirm_code() -> str:
    number = random.randint(0, 99999)
    return f"XJ{number:05d}"
