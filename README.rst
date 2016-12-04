Strainer: Fast Functional Serializers
=====================================

.. image:: https://img.shields.io/pypi/v/pystrainer.svg
    :target: https://pypi.python.org/pypi/pystrainer

.. image:: https://readthedocs.org/projects/strainer/badge/?version=latest
    :target: https://strainer.readthedocs.io/en/latest/

Strainer is a different take on serialization and validation in python.
It utilizes a functional style over inheritance.

An example of Strainer, the example is modified from the `Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ example.

Serialization Example
---------------------

.. code-block:: python

    from strainer import serializer, field, child, formatters, ValidationException

    artist_serializer = serializer(
      field('name', validations=[validators.required()])
    )

    album_schema = serializer(
      field('title', validations=[validators.required()]),
      field('release_date',
            validations=[validators.required(), validators.datetime()],
            formatters=[formatters.format_datetime()]),
      child('artist', serializer=artist_serializer, validators=[validators.required()])
    )

    class Artist(object):
        def __init__(self, name):
            self.name = name

    class Album(object):
        def __init__(self, title, release_date, artist):
            self.title = title
            self.release_date = release_date
            self.artist = artist

    bowie = Artist(name='David Bowie')
    album = Album(
        artist=bowie,
        title='Hunky Dory',
        release_date=date(1971, 12, 17)
    )

    simple_data = album_schema.deserialize({}, album)

    pprint.pprint(simple_data)

    # {'artist': {'name': 'David Bowie'},
    #  'release_date': '1971-12-17',
    #  'title': 'Hunky Dory'}

Validation Example
------------------

Give input is a simple python dict freshly decoded from raw JSON.

.. code-block:: python

  input = {
      'title': 'Hunky Dory',
      'release_date': '1971-12-17',
  }

  try:
      validated_input = question_serializer.serialize(input)
  except ValidationException as e:
      print e.errors

  # {'artist': ['This field is required']}



Installation
------------

To install Strainer, simply:

.. code-block:: bash

    $ pip install pystrainer
    ✨🍰✨

Satisfaction, guaranteed.
