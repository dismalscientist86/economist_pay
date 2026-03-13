"""
Shared utility functions for the economist_pay project.
"""


def parse_first_name(name: str) -> str:
    """
    Parse the usable first name from OPM name format.

    Handles two formats:
      - "LAST,FIRST MIDDLE"   (most agencies)
      - "LAST,,FIRST MIDDLE"  (a few agencies, double comma)

    If the first name field is a single initial, falls back to the second
    or third name token so genderize has a real name to work with.
    """
    if not isinstance(name, str) or not name.strip():
        return ""

    parts = name.split(",")

    # Determine the name portion (everything after last name)
    if len(parts) >= 3 and parts[1] == "":
        # Double-comma format: ["LAST", "", "FIRST MIDDLE"]
        name_part = parts[2].strip()
    elif len(parts) >= 2:
        name_part = parts[1].strip()
    else:
        return ""

    tokens = name_part.split()
    if not tokens:
        return ""

    firstname   = tokens[0].rstrip(".")   # strip trailing period from initials
    secondname  = tokens[1].rstrip(".") if len(tokens) > 1 else ""
    thirdname   = tokens[2].rstrip(".") if len(tokens) > 2 else ""

    # If first token is just an initial, use the next full name
    if len(firstname) <= 1:
        if len(secondname) > 1:
            return secondname
        if len(thirdname) > 1:
            return thirdname

    return firstname.title()


def parse_first_name_natural(name: str) -> str:
    """
    Parse first name from natural "First [Middle] Last" format.
    Used for PhD placement data (not OPM salary data).
    If the first token is a single initial, returns the second token.
    """
    if not isinstance(name, str) or not name.strip():
        return ""
    tokens = name.strip().split()
    if not tokens:
        return ""
    first = tokens[0].rstrip(".")
    if len(first) <= 1 and len(tokens) > 1:
        return tokens[1].rstrip(".").title()
    return first.title()


def clean_numeric(val) -> float | None:
    """
    Parse currency strings like '$120,000' or plain numbers to float.
    Returns None for unparseable values.
    """
    if val is None:
        return None
    s = str(val).replace("$", "").replace(",", "").strip()
    if not s or s in ("-", "N/A", ""):
        return None
    try:
        return float(s)
    except ValueError:
        return None
