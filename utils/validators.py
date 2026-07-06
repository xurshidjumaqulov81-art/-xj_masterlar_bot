import re

def is_valid_xj_id(xj_id: str) -> bool:
    return bool(re.fullmatch(r"\d{7}", xj_id.strip()))

def normalize_phone(phone: str) -> str:
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("998"):
        phone = "+" + phone
    return phone

def is_valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\+998\d{9}", normalize_phone(phone)))

def clean_text(text: str) -> str:
    return (text or "").strip()

