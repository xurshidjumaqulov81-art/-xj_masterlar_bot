import re


def is_valid_xj_id(xj_id: str) -> bool:
    """
    XJ ID 7 хонали рақам бўлиши керак.
    Масалан: 0012345
    """
    return bool(re.fullmatch(r"\d{7}", xj_id))


def normalize_phone(phone: str) -> str:
    """
    Телефон рақамдан ортиқча белгиларни тозалайди.
    """
    phone = phone.replace(" ", "")
    phone = phone.replace("-", "")
    phone = phone.replace("(", "")
    phone = phone.replace(")", "")
    return phone


def is_valid_phone(phone: str) -> bool:
    """
    Ўзбекистон телефон рақамини текширади.
    Масалан: +998901234567
    """
    phone = normalize_phone(phone)
    return bool(re.fullmatch(r"\+998\d{9}", phone))


def clean_text(text: str) -> str:
    """
    Матн боши ва охиридаги бўш жойларни тозалайди.
    """
    return text.strip()
