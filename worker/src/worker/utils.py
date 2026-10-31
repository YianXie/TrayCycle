from datetime import datetime


def iso_datetime_to_date(iso_datetime_str: str) -> str:
    """
    Convert an ISO 8601 datetime string to a date string in YYYY-MM-DD format.

    Args:
        iso_datetime_str (str): An ISO 8601 formatted datetime string.

    Returns:
        str: A date string in YYYY-MM-DD format.
    """
    try:
        # Parse the ISO 8601 datetime string
        dt = datetime.fromisoformat(iso_datetime_str)
        # Return the date part in YYYY-MM-DD format
        return dt.astimezone().date().isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 datetime string: {iso_datetime_str}") from e
