===============
The Network API
===============

.. contents::
    :local:

.. _auth_header:

Authorization Header
====================

All requests, except for the initial request to :ref:`connect`,
require HTTP Authorization header.

.. code-block:: http

    Authorization: Token deadbeeffadecafe

Where :code:`deadbeeffadecafe` (Dead Beef Fade Café?) is the token acquired from :ref:`connect`.
Note that there is exactly one space between :code:`Token` and the token string.
The token itself must be in lowercase and the letter T in :code:`Token` must be in uppercase.


API Endpoints
=============

.. _connect:

/api/connect
------------

Mark the robot as connected to the network.

:Request:
    :Method: POST
    :Content-Type: ``application/json``
    :Parameters:
        :id: int, the robot's id
:Response:
    :Success:
        :Status: 200
        :Content-Type: ``application/json``
        :Fields:
            :token: string, the authentication token. 16 characters hex.
    :Failure:
        :Status: 400, if the robot fails to provide its id
        :Status: 403, if a robot with the same id has connected
        :Content-Type: ``application/json``
        :Fields:
            :reason: The reason why the connection failed.
            :token: An empty string.

.. _disconnect:

/api/disconnect
---------------

Mark the robot as disconnected to the network.
Requires authorization header.

:Request:
    :Method: POST
:Response:
    :Success:
        :Status: 204
    :Failure:
        :Status: 401, the robot fails to provide a valid authentication token
        :Content-Type: ``text/plain``


.. _poll:

/api/poll
---------

The robot should use this endpoint to check if there are new messages.
Each message will only be returned once by this endpoint.

:Request:
    :Method: GET
:Response:
    :Success:
        :Status: 200
        :Content-Type: ``application/json``
        :Fields:
            :messages: A list of JSON serialized messages, which can be empty. It can always be correctly deserialized with :meth:`~crh_botnet.message.Message.from_json()`.
    :Failure:
        :Status: 401, the robot fails to provide a valid authentication token.
        :Content-Type: ``text/plain``

.. _retrieve:

/api/retrieve
-------------

:Request:
    :Method: GET
    :Fields:
        :id: The message id for retrieval
:Response:
    :Success:
        :Status: 200
        :Content-Type: ``application/json``
        :Fields:
            :message: The JSON serialized message. It can always be correctly deserialized with :meth:`~crh_botnet.message.Message.from_json()`.
    :Failure:
        :Status: 401, the robot fails to provide a valid authentication token.
        :Status: 404, a message matches the requested message id addressing to the authenticated robot does not exist.
        :Content-Type: ``text/plain``


.. _send:

/api/send
---------

The endpoint for sending a message

:Request:
    :Method: PUT
    :Content-Type: ``application/json``
    :Fields:
        :recipient: int, the id of the recipient. If recipient is -1, the message will be sent to all robots currently connected except for the sender.
        :message: The JSON serialized message. It can be obtained with :meth:`~crh_botnet.message.Message.to_json()`
:Response:
    :Success:
        :Status: 201
    :Failure:
        :Status: 404, if the recipient is not connected
        :Status: 401, if the robot fails to provide a valid authentication token.
        :Status: 403, if the message sender does not match the authenticated robot
        :Status: 400, if the robot provides an invalid message
        :Content-Type: ``text/plain``
