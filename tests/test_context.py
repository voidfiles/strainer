from strainer.context import SerializationContext


def test_context():
    ctx = SerializationContext(test_arg=True)

    assert ctx.test_arg is True
    assert ctx.none_arg is None
