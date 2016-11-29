Welcome to Strainer's documentation!
====================================

Strainer is a different take on serialization and validation in python.
It utilizes a functional style over inheritance.

An example of Strainer, the example has been borrowed from `Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_

.. code-block:: python

    artist_serializer = create_serializer(
      field('name')
    )

    album_schema = create_serializer(
      field('title'),
      field('release_date'),
      child('artist', serializer=artist_serializer)
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
    #  'release_date': datetime.date(1971, 12, 17),
    #  'title': 'Hunky Dory'}

.. toctree::
   :maxdepth: 2

   introduction
   api


