Introduction to Strainer
========================

Because Strainer was built with web applications in mind, here is an overview of Strainer that
builds on the `Django tutorial <https://docs.djangoproject.com/en/1.10/intro/tutorial01/>`_.

Background
----------

Here are the models from the tutorial.

.. code-block:: python

  from django.db import models


  class Question(models.Model):
      question_text = models.CharField(max_length=200)
      pub_date = models.DateTimeField('date published')

  class Choice(models.Model):
      question = models.ForeignKey(Question, on_delete=models.CASCADE)
      choice_text = models.CharField(max_length=200)
      votes = models.IntegerField(default=0)


We have the models, but now we want to create a JSON API for our models. We will need to serialize our models, which are rich python objects, into simple dicts so that we may conver that to JSON. First step is to create the  serializer.

Create The Serializer
---------------------

To start, we will create serializers for each model. The job of a serializer is to take a rich python object and boil it down to a simple python dict that can be eaisly converted into JSON.

.. code-block:: python

  from strainer import create_serializer, field

  question_serializer = create_serializer(
    field('question_text'),
    field('pub_date'),
  )

This is pretty straighforward. We are creating a serializer, that takes two properties from a Question model, question_text, and pub_date. Now, if we have a question model, we can convert it
into JSON like this.

.. code-block:: python

  >>> question = Question('What is the meaning of life?', pub_date=timezone.now())
  >>> question_serializer.to_representation(question)
  {
    'question_text': 'What is the meaning of life?',
    'pub_date': datetime.datetime(2016, 11, 25, 20, 13, 5, 946126)
  }

Encode The Output
-----------------

The serializer is just meant to take a set of complex python objects and reduce them to simple python dicts. You can see that pub_date is still a datetime object. The next step after serialization is to encode the result into JSON, or any other wire format of your choosing.

.. code-block:: python

  >>> from stariner.encoders import to_json
  >>> question = Question('What is the meaning of life?', pub_date=timezone.now())
  >>> print to_json(question_serializer.to_representation(question))
  {
    "question_text": "What is the meaning of life?",
    "pub_date': "2016-11-25T20:13:05.946126Z"
  }

Now that's ready to be sent back as a JSON response.

Nesting Serializers
-------------------

Next, we might want to create a JSON object that is nested. So that we have a response format that nests answers in a question.

First, we can modify our Question database model to create a new property that will return all the choices

.. code-block:: python

  class Question(models.Model):
      question_text = models.CharField(max_length=200)
      pub_date = models.DateTimeField('date published')

      @property
      def choices(self):
          return self.choice_set.all()

Next, we are going to define a Choice serializer, and then nest it in the question serializer

.. code-block:: python

  from strainer import create_serializer, field, many

  choice_serializer = create_serializer(
    field('choice_text'),
    field('votes'),
  )

  question_serializer = create_serializer(
    field('question_text'),
    field('pub_date'),
    many('choices', serializer=choice_serializer)
  )

Now, we can take a question object, that has a set of choices, and return them all in one go.

.. code-block:: python

  >>> question = Question('What is the meaning of life?', pub_date=timezone.now())
  >>> question.choice_set.create(choice_test='Chocolate')
  >>> question.choice_set.create(choice_test='42')
  >>> question_serializer.to_representation(question)
  {
    'question_text': 'What is the meaning of life?',
    'pub_date': datetime.datetime(2016, 11, 25, 20, 13, 5, 946126),
    'choices': [{
      'choice_text': 'Chocolate',
      'votes': 0
    }, {
      'choice_text': '42',
      'votes': 0
    }]
  }

This is great, we can serialize both questions and choices in an efficent, easy to use manner.

Validation
----------

This is a great start to building a JSON API, but now we want to reverse the process accept JSON. When we accept input from the outside, we first need to validate that it well-formed before we beging to work with it.

In order to do that we need to describe how our data should look with a littler more detail. We can extend our exisiting question serializer so that it will also validate data.

.. code-block:: python

  from strainer import create_serializer, field
  from strainer import validators

  question_serializer = create_serializer(
    field('question_text', validators=[
      validators.required(),
      validators.string(max_length=200),
    ]),
    field('pub_date', validators=[
      validators.required(),
      validators.datetime(),
    ]),
  )

In both cases, we are making these fields required. For question_text though we are ensuring that the input is a string, but also that it is no longer then 200 characters long. For pub_date we are ensuring that the input is a valid date and time. In this context it means that we can parse a valid ISO 8601 datetime string from the input.

If we have some JSON input, we can validate that it conforms to our expectations of the data.

.. code-block:: python

  input = {
    "question_text": "What is the meaning of life?",
    "pub_date": "2016-11-25T20:13:05Z",
  }

  validated_input = question_serializer.to_internal(input)
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
      validated_input = question_serializer.to_internal(input)
  except ValidationException as e:
      print e.errors

  # {'question_text': ['This field is to long, max length is 200']}

Here, we catch any possible validation exceptions. When a ValidationException is thrown there is a property on the exception called errors. That will have the reasons why the input is invalid. In a format that is ready to be returned as an API response.
