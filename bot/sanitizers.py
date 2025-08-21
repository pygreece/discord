from re import match as regex_match


def sanitize_user_name(name: str, id: int) -> str:
    """Checks if the name is valid and returns it in lowercase. If it isn't valid it will be replaced by the first 10 digits of the ID.

    :param str name: The name to validate.
    :param int id: The ID to use in place of the name if the name isn't valid.

    :returns str: The name in lowercase or the first 10 digits of the id.
    """
    match = regex_match(
        # Just in case
        # https://stackoverflow.com/questions/77577487/regex-expression-for-a-discord-username
        r"^(?=.{2,32}$)(?!(?:everyone|here)$)\.?[a-z0-9_]+(?:\.[a-z0-9_]+)*\.?$",
        name,
    )
    return match.group().lower() if match else str(id)[:10]


def sanitize_ticket_id(ticket_id: str) -> str:
    """Removes the hashtag and/or whitespace from the ticket ID.

    :param str ticket_id: The ticket ID string.

    :returns str: The ticket ID string with no leading "#" or any whitespace.
    """
    match = regex_match(
        # Just in case
        # https://stackoverflow.com/questions/4685500/regular-expression-for-10-digit-number-without-any-special-characters
        r"(?<!\d)\d{10}(?!\d)",
        ticket_id,
    )
    return match.group().lower() if match else ""
