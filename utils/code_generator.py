import random

def generate_confirm_code() -> str:
    return f"XJ{random.randint(0, 99999):05d}"

