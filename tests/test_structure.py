import pytest

from strainer import (field, dict_field, multiple_field, serializer, child, many, validators, ValidationException)


class ChildTestObject(object):
    b1 = 2
    c1 = 'a'


class TestObject(object):
    a = 1
    b = ChildTestObject()
    c = [ChildTestObject(), ChildTestObject()]
    d = [1, 2]


def test_field():
    serializer = field('a')
    test_obj = TestObject()
    target = {}
    serializer.serialize(test_obj, target)

    assert {'a': 1} == target

    from_json = {'a': 1}
    target = {}
    serializer.deserialize(from_json, target)

    assert {'a': 1} == target


def test_dict_field():
    serializer = dict_field('a')
    test_obj = {'a': 'b'}
    target = {}
    serializer.serialize(test_obj, target)

    assert {'a': 'b'} == target

    from_json = {'a': 'b'}
    target = {}
    serializer.deserialize(from_json, target)

    assert {'a': 'b'} == target


def test_field_custom_attr_gettr():
    serializer = field('a', attr_getter=lambda x: x.a + 1)
    test_obj = TestObject()
    target = {}
    serializer.serialize(test_obj, target)

    assert {'a': 2} == target


def test_field_multiple():
    serializer = multiple_field('d')
    test_obj = TestObject()
    target = {}
    serializer.serialize(test_obj, target)

    assert {'d': [1, 2]} == target

    from_json = {'d': [1, 2]}
    target = {}
    serializer.deserialize(from_json, target)

    assert {'d': [1, 2]} == target


def test_field_multiple_validation():
    serializer = multiple_field('e', validators=[validators.string(max_length=1)])
    test_obj = {
      'e': ['a', 'bb']
    }
    target = {}
    errors = None
    try:
        serializer.deserialize(test_obj, target)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'e': {1: ['This field is to long, max length is 1']}}


def test_serializer():
    a_serializer = serializer(
        field('a')
    )

    test_obj = TestObject()
    target = a_serializer.serialize(test_obj)

    assert {'a': 1} == target

    from_json = {'a': 1}
    target == a_serializer.deserialize(from_json)

    assert {'a': 1} == target


def test_child():
    child_serializer = serializer(
        field('b1')
    )

    a_serializer = serializer(
        field('a'),
        child('b', serializer=child_serializer)
    )

    a_dict_serializer = serializer(
        dict_field('a'),
        child('b', serializer=child_serializer, attr_getter=lambda x: x.get('b'))
    )

    test_obj = TestObject()
    target = a_serializer.serialize(test_obj)

    target2 = a_dict_serializer.serialize(test_obj.__class__.__dict__)

    assert {
      'a': 1,
      'b': {
        'b1': 2,
      }
    } == target == target2

    from_json = {
      'a': 1,
      'b': {
        'b1': 2,
      }
    }

    target = a_serializer.deserialize(from_json)

    assert from_json == target


def test_many():
    child_serializer = serializer(
        field('c1')
    )

    a_serializer = serializer(
        field('a'),
        many('c', serializer=child_serializer)
    )

    a_dict_serializer = serializer(
        dict_field('a'),
        many('c', serializer=child_serializer, attr_getter=lambda x: x.get('c'))
    )

    test_obj = TestObject()
    target = a_serializer.serialize(test_obj)
    target2 = a_dict_serializer.serialize(TestObject.__dict__)

    reference = {
      'a': 1,
      'c': [{
        'c1': 'a',
      }, {
        'c1': 'a',
      }]
    }

    assert reference == target == target2
    target = a_serializer.deserialize(reference)
    assert target == reference


def test_nested_required():
    child_serializer = serializer(
        field('c1', validators=[validators.required()])
    )

    a_serializer = serializer(
        field('a'),
        many('c', serializer=child_serializer, validators=[validators.required()])
    )

    reference = {
      'a': 1,
    }

    with pytest.raises(ValidationException):
        a_serializer.deserialize(reference)

    reference = {
      'a': 1,
      'c': [],
    }

    errors = None
    try:
        a_serializer.deserialize(reference)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'c': ['This field is required']}

    reference = {
      'a': 1,
      'c': [{}],
    }

    errors = None
    try:
        a_serializer.deserialize(reference)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'c': [{'c1': ['This field is required']}]}
