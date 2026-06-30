import re


PLATE_PATTERN = re.compile(r"^[A-Z0-9]{4,12}$")


def clean_plate_text(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def validate_plate(text: str) -> bool:
    return bool(PLATE_PATTERN.fullmatch(text))


def correct_common_ocr_errors(text: str) -> str:
    cleaned = clean_plate_text(text)
    if not cleaned:
        return cleaned

    chars = list(cleaned)
    for idx, char in enumerate(chars):
        expects_digit = idx >= max(0, len(chars) - 4)
        if expects_digit:
            chars[idx] = {"O": "0", "I": "1", "S": "5", "B": "8", "Z": "2"}.get(char, char)
    return "".join(chars)
