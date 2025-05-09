import re

def apply_regex(text, pattern):
    matches = re.findall(pattern, text)
    return matches[0] if matches else None
