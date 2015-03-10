=======
Testing
=======

Configuration
-------------

Conduction's suite tests its ability to start and stop a mongod server. To do
this it needs to know where a mongod can be found. Set the ``MONGOBIN``
environment variable to a directory containing ``mongod`` and ``mongos``, e.g.
``/usr/local/bin/``.

Test with your current Python version
-------------------------------------

    $ python setup.py test

Test all supported Python versions
----------------------------------

    $ pip install tox
    $ tox
