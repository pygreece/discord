from re import match as regex_match

def sanitize_user_name(name: str, id: int) -> str:
    match = regex_match(r'^(?=.{2,32}$)(?!(?:everyone|here)$)\.?[a-z0-9_]+(?:\.[a-z0-9_]+)*\.?$', name)
    return match.group().lower() if match else str(id)[:10]