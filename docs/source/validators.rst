.. _validators:

Validators
==========

Validators convert incoming data into the correct format, and also raise excpetions if data is invalid.

Current Validators
------------------

integer
^^^^^^^

Will validate that a value is an integer.

.. code-block:: python

  >>> from strainer import validators
  >>> int_validators = validators.integer()
  >>> int_validators('1')
  1

You can also optionally, clamp an integer to bounds

.. code-block:: python

  >>> from strainer import validators
  >>> int_validators = validators.integer(bounds=(2, 10))
  >>> int_validators('1')
  2

string
^^^^^^^

Will validate that a value is a string

.. code-block:: python

  >>> from strainer import validators
  >>> string_validators = validators.string()
  >>> int_validators(1)
  '1'


You can also apply a `max_length`. If the string is longer then the `max_length` an exception will be thrown.

.. code-block:: python

  >>> from strainer import validators
  >>> string_validators = validators.string(max_length=100)

required
^^^^^^^^

Will validate that a value exists and that it is not falsey. It will accept `0`, but raise an exception on `False`, `None`, `''`, `[]`, and `{}`.

.. code-block:: python

  >>> from strainer import validators
  >>> validators.required()

boolean
^^^^^^^

Will coerce value into either a `True`, or `False` value. `0`, `False`, `None`, `''`, '[]', and `{}` would all count as `False` values, anything else would be `True`.

.. code-block:: python

  >>> from strainer import validators
  >>> validators.boolean()

datetime
^^^^^^^^

This validator will attempt to parse an ISO 8601 string into a python datetime object.

.. code-block:: python

  >>> from strainer import validators
  >>> dt_validator = validators.datetime()
  >>> dt_validator('1984-06-11')
  datetime.datetime(1984, 6, 11)

The default timezone is UTC, but you can modify that by passing a `default_tzinfo`.


Custom Validators
-----------------

A validtora returns a function that will be used to validate a value during serialization. You can use the `export_validator` function to create a custom validation function.

.. code-block:: python

  from strainer import validators

  @formatters.export_validators
  def my_silly_validators(value, context=None):
      return '%s is silly.' % (value)

