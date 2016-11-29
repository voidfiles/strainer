"""
Structure
=========

When building a serializer, you will need certain structures.

"""
import operator

from collections import namedtuple

from .exceptions import ValidationException

Serializer = namedtuple('Serializer', 'to_representation to_internal')


def field(source_field, target_field=None, validators=None,
          multiple=False, to_representation=None):
    """Constructs an indvidual field for a serializer, this is on the
    order of one key, and one value.

    The field determines the mapping between keys internaly, and externally.
    As well as the proper validation at the level of the field.

    """
    target_field = target_field if target_field else source_field
    validators = validators if validators else []
    _to_representation = to_representation or operator.attrgetter(source_field)

    def _validate(value, field, context=None):
        errors = []
        for validator in validators:
            try:
                value = validator(value, context=context)
            except ValidationException as e:
                errors += [e.errors]

        if errors:
            raise ValidationException({
                target_field: errors
            })

    def to_representation(source, target, context=None):
        target[target_field] = _to_representation(source)

        return target

    def to_internal(source, target, context=None):
        value = source.get(target_field)

        if multiple:
            errors = {}

            for i, v in enumerate(value):
                try:
                    _validate(value, i, context=context)
                except ValidationException as e:
                    errors.update(e.errors)

            if errors:
                raise ValidationException(errors)

        else:
            _validate(value, target_field, context=context)

        target[source_field] = value

        return target

    return Serializer(to_representation, to_internal)


def child(source_field, target_field=None, serializer=None):
    """A child is a nested serializer.

    """

    target_field = target_field if target_field else source_field

    _attr_getter = operator.attrgetter(source_field)

    def to_representation(source, target, context=None):
        sub_source = _attr_getter(source)
        target[target_field] = serializer.to_representation(sub_source, context=context)

        return target

    def to_internal(source, target, context=None):
        sub_source = source.get(target_field)
        try:
            target[source_field] = serializer.to_internal(sub_source, context=context)
        except ValidationException as e:
            raise ValidationException({
                target_field: e.errors
            })

        return target

    return Serializer(to_representation, to_internal)


def many(source_field, target_field=None, serializer=None):
    """Many allows you to nest a list of serializers"""

    target_field = target_field if target_field else source_field

    _attr_getter = operator.attrgetter(source_field)

    def to_representation(source, target, context=None):
        sub_source = _attr_getter(source)

        collector = [serializer.to_representation(i, context=context) for i in sub_source]

        target[target_field] = collector

        return target

    def to_internal(source, target, context=None):
        sub_source = source.get(target_field)
        collector = []
        errors = []

        for i in sub_source:
            try:
                collector.append(serializer.to_internal(i, context=context))
            except ValidationException as e:
                errors += [e.errors]

        target[source_field] = collector

        if errors:
            raise ValidationException({
                target_field: errors
            })

        return target

    return Serializer(to_representation, to_internal)


def create_serializer(*fields):
    """This function creates a serializer from a list fo fields"""
    def to_representation(source, context=None):
        target = {}

        [field.to_representation(source, target, context=context) for field in fields]

        return target

    def to_internal(source, context=None):
        target = {}
        errors = {}

        for field in fields:
            try:
                field.to_internal(source, target, context=context)
            except ValidationException as e:
                errors.update(e.errors)

        if errors:
            raise ValidationException(errors)

        return target

    return Serializer(to_representation, to_internal)
