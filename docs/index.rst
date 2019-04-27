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

You can run the server by

.. code-block:: bash

    python3.7 -m crh_botnet.server

