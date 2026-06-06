import datetime


def get_current_utc_time():
    """Returns the current UTC time as an ISO 8601 formatted string."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def format_date(date_value):
    """Convert date to ISO format string."""
    if not date_value:
        return None
    if isinstance(date_value, str):
        return date_value
    if hasattr(date_value, 'isoformat'):
        return date_value.isoformat()
    return str(date_value)
