.. _formatters:

Formatters
==========

Formmatters help fields prepare values for serializaiton. Most formatters accept a value, and a context and return a formatted value.

Current Formatters
------------------

format_datetime
^^^^^^^^^^^^^^^

This formatter will take a datetime, or a date object and convert it into an ISO8601 string representation.

.. code-block:: python

  >>> import datetime
  >>> from strainer import formatters
  >>> dt_formatter = formatters.format_datetime()
  >>> dt_formatter(datetime.datetime(1984, 6, 11))
  '1984-06-11T00:00:00'


Custom Formatters
-----------------

A formatter returns a function that will be used to format a value before serialization, you could build a silly formatter like this.

.. code-block:: python

  def custom_formatter():
      def _my_formatter(value, context=None):
          return '%s is silly.' % (value)

      return _my_formatter

  my_formatter = custom_formatter()
  print my_formatter('A clown')
  # A clown is silly

In practice it's probably better to use the export_formatter decorator. It's as simple way to create a formatter.

.. code-block:: python

  from strainer import formatters

  @formatters.export_formatter
  def my_silly_formatter(value, context=None):
      return '%s is silly.' % (value)

It's clear, and their is less nesting.
