import pytest

from strainer import (field, dict_field, create_serializer, child, many, validators, ValidationException)


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
    serializer.to_representation(test_obj, target)

    assert {'a': 1} == target

    from_json = {'a': 1}
    target = {}
    serializer.to_internal(from_json, target)

    assert {'a': 1} == target


def test_dict_field():
    serializer = dict_field('a')
    test_obj = {'a': 'b'}
    target = {}
    serializer.to_representation(test_obj, target)

    assert {'a': 'b'} == target

    from_json = {'a': 'b'}
    target = {}
    serializer.to_internal(from_json, target)

    assert {'a': 'b'} == target


def test_field_custom_attr_gettr():
    serializer = field('a', attr_getter=lambda x: x.a + 1)
    test_obj = TestObject()
    target = {}
    serializer.to_representation(test_obj, target)

    assert {'a': 2} == target


def test_field_multiple():
    serializer = field('d', multiple=True)
    test_obj = TestObject()
    target = {}
    serializer.to_representation(test_obj, target)

    assert {'d': [1, 2]} == target

    from_json = {'d': [1, 2]}
    target = {}
    serializer.to_internal(from_json, target)

    assert {'d': [1, 2]} == target


def test_field_multiple_validation():
    serializer = field('e', multiple=True, validators=[validators.string(max_length=1)])
    test_obj = {
      'e': ['a', 'bb']
    }
    target = {}
    errors = None
    try:
        serializer.to_internal(test_obj, target)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'e': {1: ['This field is to long, max length is 1']}}


def test_serializer():
    serializer = create_serializer(
        field('a')
    )

    test_obj = TestObject()
    target = serializer.to_representation(test_obj)

    assert {'a': 1} == target

    from_json = {'a': 1}
    target == serializer.to_internal(from_json)

    assert {'a': 1} == target


def test_child():
    child_serializer = create_serializer(
        field('b1')
    )

    serializer = create_serializer(
        field('a'),
        child('b', serializer=child_serializer)
    )

    test_obj = TestObject()
    target = serializer.to_representation(test_obj)

    assert {
      'a': 1,
      'b': {
        'b1': 2,
      }
    } == target

    from_json = {
      'a': 1,
      'b': {
        'b1': 2,
      }
    }

    target = serializer.to_internal(from_json)

    assert from_json == target


def test_many():
    child_serializer = create_serializer(
        field('c1')
    )

    serializer = create_serializer(
        field('a'),
        many('c', serializer=child_serializer)
    )

    test_obj = TestObject()
    target = serializer.to_representation(test_obj)

    reference = {
      'a': 1,
      'c': [{
        'c1': 'a',
      }, {
        'c1': 'a',
      }]
    }

    assert reference == target
    target = serializer.to_internal(reference)
    assert target == reference


def test_nested_required():
    child_serializer = create_serializer(
        field('c1', validators=[validators.required()])
    )

    serializer = create_serializer(
        field('a'),
        many('c', serializer=child_serializer, validators=[validators.required()])
    )

    reference = {
      'a': 1,
    }

    with pytest.raises(ValidationException):
        serializer.to_internal(reference)

    reference = {
      'a': 1,
      'c': [],
    }

    errors = None
    try:
        serializer.to_internal(reference)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'c': ['This field is required']}

    reference = {
      'a': 1,
      'c': [{}],
    }

    errors = None
    try:
        serializer.to_internal(reference)
    except ValidationException as e:
        errors = e.errors

    assert errors == {'c': [{'c1': ['This field is required']}]}
