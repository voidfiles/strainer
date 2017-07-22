import pytest

from strainer import (field, serializer, child, many, ValidationException, validators)


class ChildTestObject(object):
    d1 = 'a'
    d2 = 'b'


class TestObject(object):
    a = 1
    b = 2
    c = 3
    d = ChildTestObject()
    e = [ChildTestObject(), ChildTestObject()]


def valid_validator(value, context=None):
    return


def nil_validator(value, context=None):
    raise ValidationException('Failed')


def nil_validator_2(value, context=None):
    raise ValidationException('Failed, again')

a_field = field('a', validators=[valid_validator, nil_validator, nil_validator_2])
b_field = field('b', validators=[valid_validator, nil_validator])
c_field = field('c', validators=[valid_validator])
d1_field = field('d1', validators=[valid_validator])
d2_field = field('d2', validators=[valid_validator, nil_validator])

a_serializer = serializer(
    a_field,
    b_field,
    c_field,
)

d_serializer = serializer(
    d1_field,
    d2_field,
)

a_serializer_with_child = serializer(
  a_field,
  child('d', serializer=d_serializer)
)

a_e_serializer = serializer(
  a_field,
  many('e', serializer=d_serializer)
)


def test_field_validation():

    from_json = {'a': 1}
    target = {}

    with pytest.raises(ValidationException):
        a_field.deserialize(from_json, target)

    try:
        a_field.deserialize(from_json, target)
    except Exception as e:
        assert hasattr(e, 'errors')
        assert e.errors == {'a': ['Failed', 'Failed, again']}


def test_serializer_validation():
    from_json = {'a': 1}

    target = None

    with pytest.raises(ValidationException):
        target = a_serializer.deserialize(from_json)

    assert target is None

    try:
        a_serializer.deserialize(from_json)
    except Exception as e:
        assert hasattr(e, 'errors')
        assert e.errors == {
            'a': ['Failed', 'Failed, again'],
            'b': ['Failed']
        }


def test_serializer_with_child_validation():
    from_json = {
      'a': 1,
      'd': {
        'd1': 'a',
        'd2': 'b'
      }
    }

    target = None

    with pytest.raises(ValidationException):
        target = a_serializer_with_child.deserialize(from_json)

    assert target is None

    try:
        a_serializer_with_child.deserialize(from_json)
    except Exception as e:
        assert hasattr(e, 'errors')
        assert e.errors == {
            'a': ['Failed', 'Failed, again'],
            'd': {
                'd2': ['Failed']
            }
        }


def test_serializer_with_many_validation():
    from_json = {
      'a': 1,
      'e': [{
        'd1': 'a',
        'd2': 'b'
      }, {
        'd1': 'a',
        'd2': 'b'
      }]
    }

    target = None

    with pytest.raises(ValidationException):
        target = a_e_serializer.deserialize(from_json)

    assert target is None

    try:
        a_e_serializer.deserialize(from_json)
    except Exception as e:
        assert hasattr(e, 'errors')
        assert e.errors == {
            'a': ['Failed', 'Failed, again'],
            'e': {
                0: {
                    'd2': ['Failed']
                },
                1: {
                    'd2': ['Failed']
                }
            }
        }


def test_validation_strings():
    a_field = field('a', validators=[validators.required(), validators.string()])
    f_field = field('f', validators=[validators.required()])
    g_field = field('g')

    a_serializer = serializer(
        a_field,
        f_field,
        g_field,
    )

    from_json = {
      'a': 1,
      'f': [],
    }

    try:
        a_serializer.deserialize(from_json)
    except Exception as e:
        assert hasattr(e, 'errors')
        assert e.errors == {
            'f': ['This field is required'],
        }
