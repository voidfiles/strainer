import pytest

from strainer.structure import field, create_serializer, child, many
from strainer.exceptions import ValidationException


class ChildTestObject(object):
    d1 = 'a'
    d2 = 'b'


class TestObject(object):
    a = 1
    b = 2
    c = 3
    d = ChildTestObject()
    e = [ChildTestObject(), ChildTestObject()]


def valid_validator(ctx, value):
    return


def nil_validator(ctx, value):
    raise ValidationException('Failed')


def nil_validator_2(ctx, value):
    raise ValidationException('Failed, again')

a_field = field('a', validators=[valid_validator, nil_validator, nil_validator_2])
b_field = field('b', validators=[valid_validator, nil_validator])
c_field = field('c', validators=[valid_validator])
d1_field = field('d1', validators=[valid_validator])
d2_field = field('d2', validators=[valid_validator, nil_validator])

a_serializer = create_serializer(
    a_field,
    b_field,
    c_field,
)

d_serializer = create_serializer(
    d1_field,
    d2_field,
)

a_serializer_with_child = create_serializer(
  a_field,
  child('d', serializer=d_serializer)
)

a_e_serializer = create_serializer(
  a_field,
  many('e', serializer=d_serializer)
)


def test_field_validation():

    from_json = {'a': 1}
    target = {}

    with pytest.raises(ValidationException):
        a_field.to_internal({}, from_json, target)

    try:
        a_field.to_internal({}, from_json, target)
    except Exception, e:
        assert hasattr(e, 'errors')
        assert e.errors == {'a': ['Failed', 'Failed, again']}


def test_serializer_validation():
    from_json = {'a': 1}

    target = None

    with pytest.raises(ValidationException):
        target = a_serializer.to_internal({}, from_json)

    assert target is None

    try:
        a_serializer.to_internal({}, from_json)
    except Exception, e:
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
        target = a_serializer_with_child.to_internal({}, from_json)

    assert target is None

    try:
        a_serializer_with_child.to_internal({}, from_json)
    except Exception, e:
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
        target = a_e_serializer.to_internal({}, from_json)

    assert target is None

    try:
        a_e_serializer.to_internal({}, from_json)
    except Exception, e:
        assert hasattr(e, 'errors')
        assert e.errors == {
            'a': ['Failed', 'Failed, again'],
            'e': [{
                'd2': ['Failed']
            }, {
                'd2': ['Failed']
            }]
        }
