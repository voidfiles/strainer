"""
Structure
=========

Use these structures to build up a serializers.

Every structure returns an object that has two methods. `serialize`
returns objects ready to be encoded into JSON, or other formats. `deserialize` will validate and
return objects ready to be used internally, or it will raise a validation
excepton.


"""
import operator
from .exceptions import ValidationException
from strainer.context import check_context


class Translator(object):
    """Translator is an internal data structure that holds a  reference to
    a serialize and deserialize function. All structures return a translator.
    """
    def __init__(self, serialize, deserialize):
        self.serialize = serialize
        self.deserialize = deserialize


def run_validators(value, full_validators, context):
    errors = []
    for validator in full_validators:
        try:
            value = validator(value, context=context)
        except ValidationException as e:
            errors += [e.errors]

    return value, errors


def emptyish(val):
    if val in [0, "", [], False]:
        return False

    if not val:
        return True

    return False


def field(source_field, target_field=None, validators=None,
          attr_getter=None, formatters=None):
    """Constructs an indvidual field for a serializer, this is on the
    order of one key, and one value.

    The field determines the mapping between keys internaly, and externally.
    As well as the proper validation at the level of the field.

    >>> from collections import namedtuple
    >>> Aonly = namedtuple('Aonly', 'a')
    >>> model = Aonly('b')
    >>> one_field = field('a')
    >>> one_field.deserialize(model)
    {'a': 'b'}

    :param str source_field: What attribute to get from a source object
    :param str target_field: What attribute to place the value on the target, optional.
                             If optional target is equal to source_field
    :param list validators: A list of validators that will be applied during deserialization.
    :param list formaters: A list of formaters that will be applied during serialization.
    :param function attr_getter: Overrides the default method for getting the soure_field off of an object
    """
    target_field = target_field if target_field else source_field
    validators = validators if validators else []
    attr_getter = attr_getter or operator.attrgetter(source_field)

    def _validate(value, field, context=None):
        value, errors = run_validators(value, validators, context)

        if errors:
            raise ValidationException({
                field: errors
            })

        return value

    def serialize(source, target, context=None):
        value = attr_getter(source)

        if formatters:
            for formater in formatters:
                value = formater(value, context)

        drop_empty = check_context(context, "drop_empty", False)
        if drop_empty and emptyish(value):
            return target

        target[target_field] = value

        return target

    def deserialize(source, target, context=None):
        value = source.get(target_field)

        value = _validate(value, target_field, context=context)

        target[source_field] = value

        return target

    return Translator(serialize, deserialize)


def multiple_field(source_field, target_field=None, validators=None,
                   attr_getter=None, formatters=None, full_validators=None):

    target_field = target_field if target_field else source_field
    validators = validators if validators else []
    attr_getter = attr_getter or operator.attrgetter(source_field)

    def _validate(value, field, context=None):
        value, errors = run_validators(value, validators, context)

        if errors:
            raise ValidationException({
                field: errors
            })

        return value

    def serialize(source, target, context=None):
        value = attr_getter(source)

        if formatters:
            for formater in formatters:
                value = formater(value, context)

        drop_empty = check_context(context, "drop_empty", False)
        if drop_empty and emptyish(value):
            return target

        target[target_field] = value

        return target

    def deserialize(source, target, context=None):
        value = source.get(target_field)

        if not value:
            value = []

        errors = {}
        new_value = []

        for i, v in enumerate(value):
            try:
                new_value += [_validate(v, i, context=context)]
            except ValidationException as e:
                errors.update(e.errors)

        value = new_value

        if full_validators:
            value, full_errors = run_validators(value, full_validators, context)
            if full_errors:
                errors.update({"_full_errors": full_errors})

        if errors:
            raise ValidationException({
                target_field: errors
            })

        target[source_field] = value

        return target

    return Translator(serialize, deserialize)


def dict_field(*args, **kwargs):
    """dict_field is just like field except that it pulls attributes
    out of a dict, instead of off an object.

    """
    kwargs.setdefault('attr_getter', lambda d: d.get(args[0]))
    return field(*args, **kwargs)


def child(source_field, target_field=None, serializer=None,
          validators=None, attr_getter=None, full_validators=None):
    """A child is a nested serializer.

    """

    target_field = target_field if target_field else source_field

    _attr_getter = attr_getter if attr_getter else operator.attrgetter(source_field)

    def serialize(source, target, context=None):
        sub_source = _attr_getter(source)

        value = serializer.serialize(sub_source, context=context)

        drop_empty = check_context(context, "drop_empty", False)
        if drop_empty and emptyish(value):
            return target

        target[target_field] = value

        return target

    def deserialize(source, target, context=None):
        sub_source = source.get(target_field)

        if validators:
            sub_source, errors = run_validators(sub_source, validators, context)

            if errors:
                raise ValidationException({
                    target_field: errors
                })

        try:
            target[source_field] = serializer.deserialize(sub_source, context=context)
        except ValidationException as e:
            raise ValidationException({
                target_field: e.errors
            })

        if full_validators:
            target, full_errors = run_validators(target, full_validators, context)
            if full_errors:
                raise ValidationException({
                    target_field: {
                        '_full_errors': full_errors,
                    }
                })

        return target

    return Translator(serialize, deserialize)


def many(source_field, target_field=None, serializer=None,
         validators=None, attr_getter=None):
    """Many allows you to nest a list of serializers"""

    target_field = target_field if target_field else source_field

    _attr_getter = attr_getter if attr_getter else operator.attrgetter(source_field)

    def serialize(source, target, context=None):
        sub_source = _attr_getter(source)

        collector = [serializer.serialize(i, context=context) for i in sub_source]

        drop_empty = check_context(context, "drop_empty", False)
        if drop_empty and emptyish(collector):
            return target

        target[target_field] = collector

        return target

    def deserialize(source, target, context=None):
        sub_source = source.get(target_field, [])
        collector = []
        errors = []

        if validators:
            sub_source, errors = run_validators(sub_source, validators, context)

            if errors:
                raise ValidationException({
                    target_field: {
                        '_full_errors': errors
                    }
                })

        error_dict = {}
        for i, item in enumerate(sub_source):
            try:
                collector.append(serializer.deserialize(item, context=context))
            except ValidationException as e:
                error_dict[i] = e.errors

        target[source_field] = collector

        if error_dict:
            raise ValidationException({
                target_field: error_dict
            })

        return target

    return Translator(serialize, deserialize)


def serializer(*fields):
    """This function creates a serializer from a list fo fields"""
    def serialize(source, context=None):
        target = {}

        [field.serialize(source, target, context=context) for field in fields]

        return target

    def deserialize(source, context=None):
        target = {}
        errors = {}

        for field in fields:
            try:
                field.deserialize(source, target, context=context)
            except ValidationException as e:
                errors.update(e.errors)

        if errors:
            raise ValidationException(errors)

        return target

    return Translator(serialize, deserialize)
