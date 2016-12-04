Structures
==========

You use structures to build up serializers.

The Field
---------

A field is the smallest structure. It maps one attribute, and one value. That value can be a list, but everything inside the list needs to be the same type.

A field shouldn't be used by its self, but you can define a field by it's self.

.. code-block:: python

  from strainer import field

  a_field = field('a')

During serialization this field will map the attribute `a` from a python object to the key `a` in a dict. During deserialization it will map a key `a` from the input to a key `a` in the ouput and validate that the value is correct.

While serializing values will be pulled in their current form from attribute to key, the reverse is not always true.

During deserialization, you can apply validators. The validators will make sure the data is in the correct form, and it will also throw an exception if the data can not be made correct.


.. code-block:: python

  from strainer import field, validators

  a_field = field('a', validators=[validators.required(), validators.string(max_length=20)])

In this code block we have defined a field that during deserialization will ensure that a is a string and that it's not longer then 20 characters.

.. code-block:: python

  >>> {'a': 'this'}  # This is valid
  >>> {'a': None}  # This is invalid because a is None
  >>> {'a': 'Supercalifragilisticexpialidocious'}  # This is invalid because it's 34 chars

You can also mark a field as being a list of values instead of one value. In this context, every value in the list must pass
validation, otherwise all the values will be rejected.

.. code-block:: python

  from strainer import field, validators

  a_field = field('a', multiple=True, validators=[validators.required(), validators.string(max_length=20)])

.. code-block:: python

  >>> {'a': ['this']}  # This is valid
  >>> {'a': ['this', None]}  # This is invalid because a is None
  >>> {'a': ['this', 'Supercalifragilisticexpialidocious']}  # This is invalid because it's 34 chars

The Serializer
--------------

A serializer bundles a bunch of fields together.

.. code-block:: python

  from strainer import serializer, field

  a_serializer = serializer(
    field('a'),
    field('b'),
  )

From here, you can serialize objects

.. code-block:: python

  >>> an_object = AnObject()
  >>> a_serializer.deserialize(an_object)
  {'a': 'a string', 'b': 1}


Nested Serializers
------------------

If you have a need for serialized nested objects, you can nest on serializer in another, using either
child, or many.

.. code-block:: python

  from strainer import serializer, field

  c_serializer = serializer(

  )

  a_serializer = serializer(
    field('a'),
    field('b'),
    child()
  )

From here, you can serialize objects

.. code-block:: python

  >>> an_object = AnObject()
  >>> a_serializer.deserialize(an_object)
  {'a': 'a string', 'b': 1}
