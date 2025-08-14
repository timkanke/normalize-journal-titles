import re

def is_valid_issn(item):
    pattern = re.compile(r"^\d{4}-?\d{3}[\dX]$")
    return bool(pattern.match(item))

def remove_non_issn(issn_column):
    return [item for item in issn_column if is_valid_issn(item)]


def is_valid_isbn(item):
    if not isinstance(item, str):
        return False
    # Remove hyphens and spaces
    item = item.replace("-", "").replace(" ", "")
    # Check for ISBN-10 format
    if re.match(r"^\d{9}[\dX]$", item):
        return True
    # Check for ISBN-13 format
    if re.match(r"^\d{13}$", item):
        return True
    return False

def remove_non_isbn(issn_column):
    return [item for item in issn_column if is_valid_isbn(item)]