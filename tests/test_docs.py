import iso8601
import datetime
from strainer import serializer, field, child, formatters, validators


def test_docs():

    artist_serializer = serializer(
      field('name', validators=[validators.required()])
    )

    album_schema = serializer(
      field('title', validators=[validators.required()]),
      field('release_date',
            validators=[validators.required(), validators.datetime()],
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
        release_date=datetime.datetime(1971, 12, 17)
    )

    assert album_schema.serialize(album) == {
      'artist': {'name': 'David Bowie'},
      'release_date': '1971-12-17T00:00:00',
      'title': 'Hunky Dory'
    }
    assert album_schema.deserialize(album_schema.serialize(album)) == {
      'artist': {'name': 'David Bowie'},
      'release_date': datetime.datetime(1971, 12, 17, 0, 0, tzinfo=iso8601.UTC),
      'title': 'Hunky Dory'
    }
    input = album_schema.serialize(album)
    del input['artist']
    errors = None
    try:
        album_schema.deserialize(input)
    except Exception as e:
        errors = e.errors

    assert errors == {'artist': ['This field is required']}
