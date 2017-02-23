Introduction to Strainer
========================

Strainer was built with restful api's in mind. Here is an informal overview of how to use strainer in that domain.

The goal of this document is to give you enough technical specifics to understand how Strainer works, but this isn’t intended to be a tutorial or reference. Once you have your bearings dive into the more technical parts of the documentation.

Background
----------

Strainer was built to serialize rich Python objects into simple data structures. You might use Strainer with an object relation mapper like Django's ORM, or SQLAlchemy. So, first we are going to define some models that we will use for the rest of the introduction.

We are going to cover some aspects of creating an API that will track RSS feeds and their items. Here are two simple models that could represent RSS feeds and their items.

.. code-block:: python

  class Feed(object):
      def __init__(self, feed, name, items):
          self.feed = feed
          self.name = name
          self.items = items

  class FeedItem(object):
      def __init__(self, title, pub_date):
          self.title = title
          self.pub_date = pub_date

We have the models, but now we want to create a JSON API for our models. We will need to serialize our models, which are rich python objects, into simple dicts so that we may convert them into JSON. First step is to create the  serializer.

Create A Feed Serializer
------------------------

To start, we will create serializers for each model. The job of a serializer is to take a rich python object and boil it down to a simple python dict that can be eaisly converted into JSON. Given the Feed model we just created, a serializer might look like this.

.. code-block:: python

  from strainer import serializer, field, formatters, validators

  feed_serializer = serializer(
    field('feed', validators=[validators.required()]),
    field('name', validators=[validators.required()]),
  )

This serializer will map the feed, and name attributes into a simple python dict. Now, we can nest the item serializer into the feed serializer, here's how.

.. code-block:: python

  from strainer import serializer, field, many, formatters, validators

  feed_item_serializer = serializer(
    field('title', validators=[validators.required()]),
    field('pub_date', validators=[validators.required(), validators.datetime()],
          formatters=[formatters.format_datetime()]),
  )

  feed_serializer = serializer(
    field('feed', validators=[validators.required()]),
    field('name', validators=[validators.required()]),
    many('items', serializer=feed_item_serializer),
  )

Using A Feed Serializer
-----------------------

We can now use the serializer. We first can instantiate some models, and then we will serialize them into dicts.


.. code-block:: python

  >>> import datetime
  >>> feed_items = [FeedItem('A Title', datetime.datetime(2016, 11, 10, 10, 15))]
  >>> feed_items += [FeedItem('Another Title', datetime.datetime(2016, 11, 10, 10, 20))]
  >>> feed = Feed('http://example.org/feed.xml', 'A Blog', feed_items)
  >>> feed_serializer.serialize(feed)
  {'feed': 'http://example.org/feed.xml',
   'items': [{'pub_date': '2016-11-10T10:15:00', 'title': 'A Title'},
    {'pub_date': '2016-11-10T10:20:00', 'title': 'Another Title'}],
   'name': 'A Blog'}

At this point, if we had REST API, we could convert this simple data structure into JSON and return it as the response body.

Validation
----------

This is a great start to building a JSON API, but now we want to reverse the process and accept JSON. When we accept input from the outside, we first need to validate that it well-formed before we begin to work with it.

Since, we have already described our data, including what makes it valid, we can use our existing serializer, just in reverse. So, let's say we are going to create feed item, we can do the following

.. code-block:: python

  feed_item = {
      'title': 'A Title',
      'pub_date': '2016-11-10T10:15:00',
  }
  print feed_item_serializer.deserialize(feed_item)
  # {'pub_date': datetime.datetime(2016, 11, 10, 10, 15, tzinfo=<iso8601.Utc>), 'title': 'A Title'}


At this point, we could take that deserialized input and instantiate a FeedItem oject. If we were using an ORM we could then persist that object to the database.

Error Reporting
---------------

Data will not always be valid, and when it isn't valid we should be able to report those errors back the user agent. So, we need a way to catch and present errors.

.. code-block:: python

  from strainer import ValidationException

  feed_item = {
    'title': 'A Title',
  }

  try:
    feed_item_serializer.deserialize(feed_item)
  except ValidationException, e:
    print e.errors

  # {'pub_date': ['This field is required']}

Here, we catch any possible validation exceptions. When a ValidationException is thrown there is a property on the exception called errors. That will have the reasons why the input is invalid. In a format that is ready to be returned as an API response.
