from strainer import serializer, field, child, many


def test_back_and_fourth():
    class Object1(object):
        c = 'b'

    class Object2(object):
        a = 2
        b = Object1()
        d = [Object1(), Object1()]

    obj = Object2()

    serializer1 = serializer(
        field('c')
    )

    serializer3 = serializer(
        field('a'),
        child('b', serializer=serializer1),
        many('d', serializer=serializer1),
    )

    json_data = {'a': 2, 'b': {'c': 'b'}, 'd': [{'c': 'b'}, {'c': 'b'}]}

    serialized_data = serializer3.serialize(obj)
    assert serialized_data == json_data
    assert serialized_data == serializer3.deserialize(json_data)
