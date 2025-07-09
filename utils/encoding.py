import chardet
from typing import Union

def detect_encoding(data: bytes) -> str:
    result = chardet.detect(data)
    encoding = result.get("encoding")
    return encoding if encoding is not None else "utf-8"
