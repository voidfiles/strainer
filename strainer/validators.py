from functools import partial, wraps
from .exceptions import ValidationException


def export_validator(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        return partial(f, *args, **kwargs)

    return wrapper


def clamp_to_interval(value, bounds):
    min_bound, max_bound = bounds
    return min(max_bound, max(min_bound, value))


@export_validator
def integer(value, bounds=None, context=None):
    """converts a value to integer, applying optional bounds
    """
    try:
        value = int(value)
        if bounds:
            return clamp_to_interval(value, bounds)
        return value
    except (TypeError, ValueError):
        raise ValidationException('This field is not an integer')


@export_validator
def string(value, context=None):
    try:
        return unicode(value)
    except (TypeError, ValueError):
        raise ValidationException('This field is a string')


@export_validator
def required(value, context=None):
    if value is 0:
        return value

    if not value:
        raise ValidationException('This field is required')

    return value


@export_validator
def boolean(value, context=None):
    try:
        return bool(value)
    except (TypeError, ValueError):
        raise ValidationException('This field is suppose to be boolean')
