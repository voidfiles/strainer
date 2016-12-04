Introduction to Strainer
========================

Because Strainer was built with web applications in mind, here is an overview of Strainer that
borrows from the `Django tutorial <https://docs.djangoproject.com/en/1.10/intro/tutorial01/>`_.

Background
----------

Here are the models we will use.

.. code-block:: python

  class Question(object):
      def __init__(self, question_text, pub_date, choices)
          self.question_text = question_text
          self.pub_date = pub_date
          self.choices = choices

  class Choice(object):
      def __init__(self, choice_text, votes):
          self.choice_text = choice_text
          self.votes = votes


We have the models, but now we want to create a JSON API for our models. We will need to serialize our models, which are rich python objects, into simple dicts so that we may convert them into JSON. First step is to create the  serializer.

Create The Serializer
---------------------

To start, we will create serializers for each model. The job of a serializer is to take a rich python object and boil it down to a simple python dict that can be eaisly converted into JSON.

.. code-block:: python

  from strainer import serializer, field, formatters

  question_serializer = serializer(
    field('question_text'),
    field('pub_date', formatters=[formatters.format_datetime()]),
  )

This is pretty straighforward. We are creating a serializer, that takes two properties from a Question model, question_text, and pub_date. Now, if we have a question model, we can convert it into JSON like this.

.. code-block:: python

  >>> question = Question('What is the meaning of life?', pub_date=datetime.utcnow())
  >>> question_serializer.deserialize(question)
  {
    'question_text': 'What is the meaning of life?',
    'pub_date': '2016-11-25T20:13:05.946126',
  }

This output can eaisly be encoded into JSON, or any other wire format you may choose to use.

Nesting Serializers
-------------------

We want to returna JSON response that has a question object, with nested choice objects.

We need to define Choice serializer, and then nest it in the question serializer.

.. code-block:: python

  from strainer import serializer, field, many, formatters

  choice_serializer = serializer(
    field('choice_text'),
    field('votes'),
  )

  question_serializer = serializer(
    field('question_text'),
    field('pub_date', formatters=[formatters.format_datetime()]),
    many('choices', serializer=choice_serializer)
  )

Now, we can take a question object, that has a set of choices, and return them all in one go.

.. code-block:: python

  >>> choices = [Choice(choice_test='Chocolate', votes=0)]
  >>> choices.append(Choice(choice_test='42', votes=0))
  >>> question = Question('What is the meaning of life?', pub_date=timezone.now(), choices=choices)
  >>> question_serializer.deserialize(question)
  {
    'question_text': 'What is the meaning of life?',
    'pub_date': '2016-11-25T20:13:05.946126',
    'choices': [{
      'choice_text': 'Chocolate',
      'votes': 0
    }, {
      'choice_text': '42',
      'votes': 0
    }]
  }

Validation
----------

This is a great start to building a JSON API, but now we want to reverse the process and accept JSON. When we accept input from the outside, we first need to validate that it well-formed before we beging to work with it.

In order to do that we need to describe how our data should look with a littler more detail. We can extend our exisiting question serializer so that it will also validate data.

.. code-block:: python

  from strainer import serializer, field, validators, formatters

  question_serializer = serializer(
    field('question_text', validators=[
      validators.required(),
      validators.string(max_length=200),
    ]),
    field('pub_date', validators=[
      validators.required(),
      validators.datetime(),
    ], formatters=[formatters.format_datetime()]),
  )

In both cases, we are making these fields required. For question_text though we are ensuring that the input is a string, but also that it is no longer then 200 characters long. For pub_date we are ensuring that the input is a valid date and time. In this context it means that we can parse a valid ISO 8601 datetime string from the input.

If we have some JSON input, we can validate that it conforms to our expectations of the data.

.. code-block:: python

  input = {
    "question_text": "What is the meaning of life?",
    "pub_date": "2016-11-25T20:13:05Z",
  }

  validated_input = question_serializer.serialize(input)
  print validated_input

  # {
  #   "question_text": "What is the meaning of life?",
  #   "pub_date": datetime.datetime(2016, 11, 25, 20, 13, 5, tzinfo=<iso8601.Utc>)
  # }

So, now we have taken raw JSON and confirmed that it is valid, for more information on handling validation take a look at Validations.

Error Reporting
---------------

Data will not always be valid, and when it isn't valid we should be able to report those errors back the user agent. So, we need a way to catch and present errors.

.. code-block:: python

  from strainer.exceptions import ValidationException

  input = {
    "question_text": "a" * 201,
    "pub_date": "2016-11-25T20:13:05Z",
  }

  try:
      validated_input = question_serializer.serialize(input)
  except ValidationException as e:
      print e.errors

  # {'question_text': ['This field is to long, max length is 200']}

Here, we catch any possible validation exceptions. When a ValidationException is thrown there is a property on the exception called errors. That will have the reasons why the input is invalid. In a format that is ready to be returned as an API response.
