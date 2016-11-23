"""
Structure
=========

When building a serializer, you will need certain structures

"""
import operator

from collections import namedtuple

from .exceptions import ValidationException

Serializer = namedtuple('Serializer', 'to_representation to_internal')


def field(source_field, target_field=None, validators=None, multiple=False):
    """field

    Constructs an indvidual field for a serializer, this is on the
    order of one key, and one value.

    The field determines the mapping between keys internaly, and externally.
    As well as the proper validation at the level of the field.

    """
    target_field = target_field if target_field else source_field
    validators = validators if validators else []

    def _validate(ctx, value, field):
        errors = []
        for validator in validators:
            try:
                validator(ctx, value)
            except ValidationException, e:
                errors += [e.errors]

        if errors:
            raise ValidationException({
                target_field: errors
            })

    _attr_getter = operator.attrgetter(source_field)

    def to_representation(ctx, source, target):
        target[target_field] = _attr_getter(source)

        return target

    def to_internal(ctx, source, target):
        value = source.get(target_field)

        if multiple:
            errors = {}

            for i, v in enumerate(value):
                try:
                    _validate(ctx, value, i)
                except ValidationException, e:
                    errors.update(e.errors)

            if errors:
                raise ValidationException(errors)

        else:
            _validate(ctx, value, target_field)

        target[source_field] = value

        return target

    return Serializer(to_representation, to_internal)


def child(source_field, target_field=None, serializer=None):
    target_field = target_field if target_field else source_field

    _attr_getter = operator.attrgetter(source_field)

    def to_representation(ctx, source, target):
        sub_source = _attr_getter(source)
        target[target_field] = serializer.to_representation(ctx, sub_source)

        return target

    def to_internal(ctx, source, target):
        sub_source = source.get(target_field)
        try:
            target[source_field] = serializer.to_internal(ctx, sub_source)
        except ValidationException, e:
            raise ValidationException({
                target_field: e.errors
            })

        return target

    return Serializer(to_representation, to_internal)


def many(source_field, target_field=None, serializer=None):
    target_field = target_field if target_field else source_field

    _attr_getter = operator.attrgetter(source_field)

    def to_representation(ctx, source, target):
        sub_source = _attr_getter(source)
        collector = []
        for i in sub_source:
            collector.append(serializer.to_representation(ctx, i))

        target[target_field] = collector

        return target

    def to_internal(ctx, source, target):
        sub_source = source.get(target_field)
        collector = []
        errors = []

        for i in sub_source:
            try:
                collector.append(serializer.to_internal(ctx, i))
            except ValidationException, e:
                errors += [e.errors]

        target[source_field] = collector

        if errors:
            raise ValidationException({
                target_field: errors
            })

        return target

    return Serializer(to_representation, to_internal)


def create_serializer(*fields):
    def to_representation(ctx, source):
        target = {}

        for field in fields:
            field.to_representation(ctx, source, target)

        return target

    def to_internal(ctx, source):
        target = {}
        errors = {}

        for field in fields:
            try:
                field.to_internal(ctx, source, target)
            except ValidationException, e:
                errors.update(e.errors)

        if errors:
            raise ValidationException(errors)

        return target

    return Serializer(to_representation, to_internal)
