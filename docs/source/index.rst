Welcome to Strainer's documentation!
====================================

Strainer is a different take on serialization and validation in python.
It utilizes a functional style over inheritance.

An example of Strainer, the example has been borrowed from `Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_

.. code-block:: python

    from strainer import create_serializer, field, child, formatters, ValidationException

    artist_serializer = create_serializer(
      field('name', validations=[validators.required()])
    )

    album_schema = create_serializer(
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

    simple_data = album_schema.to_representation({}, album)

    pprint.pprint(simple_data)

    # {'artist': {'name': 'David Bowie'},
    #  'release_date': '1971-12-17',
    #  'title': 'Hunky Dory'}

.. toctree::
   :maxdepth: 2

   introduction
   structure
   api


