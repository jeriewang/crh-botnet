========================
CRH BotNet Documentation
========================

:Author: Jerry Wang
:Date: April 2019

This package is developed for classroom purpose for Autonomous Robotics (CS570HO) class at Choate Rosemary Hall. It is intended to simulate an Arduino environment while enabling robots communicating with each other via the Internet (or the LAN).

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    introduction
    examples
    robot
    message
    network
    server

Installation
============

You can install the package by simply using your favorite package manager, ``pip``.

Supports Python3.7+

.. code-block:: bash

    python3.7 -m pip install crh-botnet

Or from source

.. code-block:: bash

    git clone https://github.com/pkqxdd/crh-botnet.git
    cd crh-botnet
    python3.7 setup.py install

Running The Server
==================

You can run the server by

.. code-block:: bash

    python3.7 -m crh_botnet.server

You can also change the port and/or the address you are listening to

.. code-block:: bash

    python3.7 -m crh_botnet.server -h 127.0.0.1 -p 8000

The default host is :code:`0.0.0.0` and the default port is :code:`5003`

