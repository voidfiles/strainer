from strainer.context import SerializationContext, check_context


def test_context():
    ctx = SerializationContext(test_arg=True)

    assert ctx.test_arg is True


def test_check_context():
    ctx = SerializationContext(test_arg=True)

    assert check_context(ctx, 'test_arg', False) is True
    assert check_context(ctx, 'none_arg', True) is True
