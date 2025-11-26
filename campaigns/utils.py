import re
import pandas as pd

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip().lower()))

def is_excel_file(filename: str) -> bool:
    return filename.lower().endswith((".xlsx", ".xls"))
