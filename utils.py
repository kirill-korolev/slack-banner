import re

def is_keyword_in_string(substr: str, fullstr: str):
    return True if fullstr.find(substr) != -1 else False


def is_wallet_in_string(fullstr: str):
    pattern = re.compile(r'0[xX][0-9a-zA-Z]+', re.MULTILINE)
    res = pattern.search(fullstr)

    if res is None:
        return False
    else:
        return True

def get_user_name(text: str):
    text = text.rstrip()
    res = re.search(r'\|(.*?)>', text)

    if res is not None:
        return res.group(1)