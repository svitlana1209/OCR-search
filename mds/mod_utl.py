import re

def normolize_string(some_text):
    r = re.sub(r"[\"\n\|\t\v]", " ", some_text)
    r = " ".join(r.split())
    r.strip()
    return r

