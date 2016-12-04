from datetime import date
from strainer import serializer, field, child, formatters


def test_docs():

    artist_serializer = serializer(
      field('name')
    )

    album_schema = serializer(
      field('title'),
      field('release_date', formatters=[formatters.format_datetime()]),
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

    simple_data = album_schema.serialize(album)

    assert simple_data == {
      'artist': {'name': 'David Bowie'},
      'release_date': '1971-12-17',
      'title': 'Hunky Dory'
    }
