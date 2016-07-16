Bazooka - reliable HTTP client
==============================

.. image:: https://travis-ci.org/phantomii/bazooka.svg?branch=master
    :target: https://travis-ci.org/phantomii/bazooka

Features:

  * retries out of box
  * full-compatible interface with requests
  * by default client raises exception if status code isn't 2xx
  * curl-like logging out of box
  * correlation-id support
  * Telstra-authentication support


Example
=======

>>  from bazooka import client
>>
>>  c = client.Client('basic-auth-token',
>>                    'auth-user-token',
>>                    'correlation id or None')
>>
>>  print c.get('http://eis/').json()

or

>>  import bazooka
>>
>>  c = bazooka.Client(...)


Duration logging is enabled by default for client.
You can use log_duration flag to enable duration logging

>>  c = client.Client('basic-auth-token',
>>                    'auth-user-token',
>>		    'correlation id or None',
>>		    log_duration=False)

  or

>>  c.log_duration = False

TODO
====

  * timeouts support
