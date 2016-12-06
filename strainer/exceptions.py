"""
Exceptions
========

This is just a set of utilities to help take a deserialized dict and turn it into JSON. It handles things like datetime objects.
"""
from six import text_type


class ValidationException(Exception):
    """This exception keeps track of all the exceptions thrown during validations
    """
    def __init__(self, errors):
        super(ValidationException, self).__init__()
        self.errors = errors

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return text_type(self.errors)
