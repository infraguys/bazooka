Bazooka - reliable HTTP client
==============================

.. image:: https://github.com/infraguys/bazooka/actions/workflows/tests.yaml/badge.svg
    :target: https://github.com/infraguys/bazooka/actions/workflows/tests.yaml

Features:

* retries out of box
* full-compatible interface with requests
* by default client raises exception if status code isn't 2xx
* curl-like logging out of box
* correlation-id support


Example
=======

.. code-block:: python

  >>  from bazooka import client
  >>
  >>  c = client.Client()
  >>
  >>  print c.get('http://eis/').json()

or

.. code-block:: python

  >>  import bazooka
  >>
  >>  c = bazooka.Client(...)


Duration logging is enabled by default for client.
You can use log_duration flag to enable duration logging

.. code-block:: python

  >>  c = client.Client(log_duration=False)

or

.. code-block:: python

  >>  c.log_duration = False
