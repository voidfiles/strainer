"""
Encoders
========

This is just a set of utilities to help take a deserialized dict and turn it into JSON. It handles things like datetime objects.
"""
import datetime
import json


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation
        elif isinstance(obj, datetime.date):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)


def to_json(*args, **kwargs):
    """accepts data and converts it into a JSON object.
    """
    kwargs.setdefault('cls', JSONEncoder)
    return json.dumps(*args, **kwargs)
