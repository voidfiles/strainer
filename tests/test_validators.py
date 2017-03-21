import pytest
import datetime

from strainer import (validators, ValidationException)


def test_integer():
    validator = validators.integer()
    assert validator(1) == 1
    assert validator('1') == 1

    with pytest.raises(ValidationException):
        validator(None)

    validator = validators.integer(bounds=(10, 15))
    assert validator('9') == 10
    assert validator('10') == 10
    assert validator('15') == 15
    assert validator('16') == 15


def test_string():
    validator = validators.string()
    assert validator('1') == '1'
    assert validator(1) == '1'
    assert validator(None) == None
    assert validator([]) == []
    assert validator({}) == {}

    validator = validators.string(max_length=5)

    assert 'a' * 5 == validator('a' * 5)
    with pytest.raises(ValidationException):
        validator('a' * 6)


def test_required():
    validator = validators.required()
    assert '1' == validator('1')

    with pytest.raises(ValidationException):
        validator(None)

    with pytest.raises(ValidationException):
        validator('')

    assert validator(False) is False

    for zero in [0, 0.0, 0j]:
        assert validator(zero) == zero


def test_boolean():
    validator = validators.boolean()
    assert True is validator('1')
    assert True is validator(1)
    assert True is validator(True)
    assert False is validator('')
    assert False is validator([])
    assert False is validator({})
    assert False is validator(False)
    assert False is validator(None)
    assert False is validator(0)


def test_datetime():
    validator = validators.datetime()
    assert type(validator('1970-01-01')) is datetime.datetime
    assert validator('') is None
    assert validator(None) is None
