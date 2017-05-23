"""
Serialization Context
=====================

When we run a serialization, or a deserialization there are small
things we want to tweak for the whole operation.

This context object is a way to pass information into the whole
process.


"""


class SerializationContext(object):
    def __init__(self, *args, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def check_context(context, key, default=None):
    if not context:
        return default

    return getattr(context, key, default)
