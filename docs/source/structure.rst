Structures
==========

Strainer exists to convert data structures comprised of rich python objects into simple datastructures ready to be converted into something suitable for HTTP resposes. It also exsists to take those simple data structures back to rich python types, and validate that the data is what it's suppose to be.

The meat of that serialization is strainers structures. They descrbe the entire process from serialization, to validation, to deserialization.

The Basics of Structures
------------------------

All structures return a `Translator` object. `Translator` objects have only two methods. `.serialize` will turn rich python objects into simple python data structures, and `.deserialize` will validate, and turn simple data structures into righ python types.

You can compose comples serializers by combining a number of structures.

The Field
---------

A field is the smallest structure. It maps one attribute, and one value. That value can be a list, but everything inside the list needs to be the same type.

A field shouldn't be used by its self, but you can define a field by it's self.

.. code-block:: python

  from strainer import field

  a_field = field('a')

During serialization this field will map the attribute `a` from a python object to the key `a` in a dict. During deserialization it will map a key `a` from the input to a key `a` in the ouput and validate that the value is correct.

Target Field
^^^^^^^^^^^^

Sometimes, the field name in the output isn't always the same as the attribute name in the input. So, you can pass a second optional argument to achieve different names.

.. code-block:: python

  from strainer import field

  a_field = field('a', target_field='z')

Now `a_field` will serialize the attribute `a` to the field `z` in the output, and during deserialization the reverse will happen. All structures have the target_field argument.

Validators
^^^^^^^^^^

When deserializing a structure you can have a series of validators run, validtors server two functions. The first is too convert incoming data into the correct form if possible, and the second is to validate that the incoming data is correct. Validators are always run when deserialization is called, and they are only run during deserialization. Validators are called in order.

.. code-block:: python

  from strainer import field, validators

  a_field = field('a', validators=[validators.required(), validators.string(max_length=10)])

Read more about validators see, :ref:`validators`.

Multiple Values
^^^^^^^^^^^^^^^

It is possible to declare a field as a list instead of single value. If you do so each value in the list will be validated as a single value. If any fail, the validation will fail.

.. code-block:: python

  from strainer import multiple_field, validators

  a_field = multiple_field('a')

Custom Attribute Getter
^^^^^^^^^^^^^^^^^^^^^^^

The default method for geting attributes from objects is to use the `operator.attrgetter` function. You can pass in a different function.

This will attempt to fetch a key from a dict instead of using attrgetter.

.. code-block:: python

  from strainer import field

  a_field = field('a', attr_getter=lambda x: x.get('a'))

Format A Value For Serialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the value that is fetched from the attribute of the object is passed forward as-is, but you can format values for serialization by passing in a list of formatters.

.. code-block:: python

  from strainer import field, validators, formatters

  a_field = field('a', validators=[validators.datetime()], formatters=[formatters.format_datetime()])

Read more about formatters, see , :ref:`formatters`.

The Dict Field
--------------

The dict_field is almost exactly like the field, except that it will attempt to get a key from a dict instead of an attribute from an object.

.. code-block:: python

  from strainer import dict_field

  a_field = dict_field('a')


The Child
---------

When creating a serializer, often one will need to model one object nested in another object. This is where the `child` strucutre comes handy. It allows you to nest one serializer in another.

.. code-block:: python

  from strainer import serializer, field, child

  c_serializer = serializer(
    field('c1'),
  )

  a_serializer = serializer(
    field('b'),
    child('c', serializer=c_serializer),
  )

Target Field
^^^^^^^^^^^^

Sometimes, the field name in the output isn't always the same as the attribute name in the input. So, you can pass a second optional argument to achieve different names.

.. code-block:: python

  from strainer import serializer, field

  c_serializer = serializer(
    field('c1'),
  )

  a_serializer = serializer(
    field('b'),
    child('c', target_field='a', serializer=c_serializer),
  )

Now `a_serializer` will serialize the attribute `c` to the field `a` in the output, and during deserialization the reverse will happen.

Validators
^^^^^^^^^^

Just like the regular field, you can apply validations to a child structure. These validators run before the inner object is deserialized it's self.

In this example you may want to require that the child object exists.

.. code-block:: python

  from strainer import serializer, field, validators

  c_serializer = serializer(
    field('c1'),
  )

  a_serializer = serializer(
    field('b'),
    child('c', validators=[validators.required()], serializer=c_serializer),
  )


The Many
--------

The Many structure is like the Child structure. It allows you to nest objects. The Many though allows you to nest an array of values instead of one. Like the child strucutre you can also use validators.

.. code-block:: python

  from strainer import many, serializer, field, validators

  c_serializer = serializer(
    field('c1'),
  )

  a_serializer = serializer(
    field('b'),
    many('c', validators=[validators.required()], serializer=c_serializer),
  )

One thing to keep in mind is that the passed validators to many will be passed all the data in the target key. That way you can perform validation over the whole structure. For instance you could limit the length of a list. The full validation will happen before the data is passed to the serialier.

The Serializer
--------------

A serializer is composed of any number of Translators, usually produce by other structures like field, child, and many. The serializer returns a translator object that can serializer, and deserialize.

.. code-block:: python

  from strainer import serializer, field

  a_serializer = serializer(
    field('a'),
    field('b'),
  )




