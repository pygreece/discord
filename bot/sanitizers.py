from re import match as regex_match


def sanitize_user_name(name: str, id: int) -> str:
    """Checks if the name is valid and returns it in lowercase. If it isn't valid it will be replaced by the first 10 digits of the ID.

    Args:
        name (str): The name to validate.
        id (int): The id to replace the name if it isn't valid.

    Returns:
        str: The name in lowercase or the first 10 digits of the id.
    """
    match = regex_match(
        r"^(?=.{2,32}$)(?!(?:everyone|here)$)\.?[a-z0-9_]+(?:\.[a-z0-9_]+)*\.?$", name
    )
    return match.group().lower() if match else str(id)[:10]

def sanitize_ticket_id(ticket_id: str) -> str:
    """Removes the hashtag and/or whitespace from the ticket ID.

    Args:
        ticket_id (str): The ticket ID.

    Returns:
        str: The ticket ID.
    """
    return ticket_id.strip().split("#")[-1]