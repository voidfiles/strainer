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
    kwargs.setdefault('cls', JSONEncoder)
    return json.dumps(*args, **kwargs)
