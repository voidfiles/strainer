"""
Formatters
==========

Formatters are functions that transform data.

"""
import datetime
from functools import partial, wraps


def export_formatter(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        return partial(f, *args, **kwargs)

    return wrapper


@export_formatter
def format_datetime(value, context=None):
    """Formats a value as an iso8601 datetime
    """
    if not value:
        return value

    if isinstance(value, datetime.datetime):
        representation = value.isoformat()
        if representation.endswith('+00:00'):
            representation = representation[:-6] + 'Z'
        return representation
    elif isinstance(value, datetime.date):
        return value.isoformat()

    return value
