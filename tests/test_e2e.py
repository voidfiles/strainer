from strainer import create_serializer, field, child, many


def test_back_and_fourth():
    class Object1(object):
        c = 'b'

    class Object2(object):
        a = 2
        b = Object1()
        d = [Object1(), Object1()]

    obj = Object2()

    serializer1 = create_serializer(
        field('c')
    )

    serializer3 = create_serializer(
        field('a'),
        child('b', serializer=serializer1),
        many('d', serializer=serializer1),
    )

    json_data = {'a': 2, 'b': {'c': 'b'}, 'd': [{'c': 'b'}, {'c': 'b'}]}

    serialized_data = serializer3.to_representation({}, obj)
    assert serialized_data == json_data
    assert serialized_data == serializer3.to_internal({}, json_data)
