.. :changelog:

Release History
---------------


1.0.1
++++++++++

- refining validators
- added attr_getter to child, and many

1.0.0
++++++++++

- Updating docs
- Making it official

0.0.9
++++++++++++++++++

* Fixing python 3 comptatability issue

0.0.8
++++++++++++++++++

* Removed an errant print statement

0.0.7
++++++++++++++++++

* Fixed a bug with datetime validators

0.0.6
++++++++++++++++++

* Fixed a bug with multiple validation, pointing to the correct index
* Fixed a bug that applied vlaidation to entire array in multiple instead of elements
* Added a dict_field, if source is dict, instead of an object
* Added ability to pass validators to child, and many instances applying validation before moving to sub-element
* Added tests around catching nested validation errors
* Added formatters, so things can be formatted on the way out
* Got rid of encoders, not the domain of this project
* Everything can be imported from one namespace
* Changed the API from to_representation/to_internal to serialize/deserialize

0.0.5 (2016-11-29)
++++++++++++++++++

* Fleshed out docs
* Added datetime validator
* Increased speed bu reducing loops

0.0.4 (2016-11-23)
++++++++++++++++++

* Add some validators


0.0.1 (2016-11-23)
++++++++++++++++++

* Birth
