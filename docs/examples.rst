.. _examples:

Examples
========

For all the examples here, it is assumed that the server is ran with

.. code-block:: bash

    sudo python3.7 -m crh_botnet.server -p 80

and that it is addressable by :code:`choate-robotics-rpi-01.local`. Please
adjust as necessary.

Say Hi To Another Robot
-----------------------

This is probably the most straightforward example.

.. literalinclude:: examples/say_hi.py

When this robot is connected, it will send a message to all other connected
robots, who will send a simple "Hi to you too" back. Note that this program
does not define a :code:`loop()` function.

Simple LED Cycler
-----------------

This is a simple implementation that two robots alternate turning on LEDs,
0.5 seconds each.

.. literalinclude:: examples/led_cycler_simple.py

In order to achieve the delay, :code:`on_message()` is defined to be async.
Also, the coroutine version of broadcast is used, which will give a smoother
blink on slow network (although pretty much no difference on fast network).

Complex LED Cycler
------------------

This implementation does the same as above, except that it supports multiple
robots.

.. literalinclude:: examples/led_cycler.py
    :emphasize-lines: 20

The reason for the re-fetch at line 20 is that the robot will keep updating
the list of connected robots during a sleep, and it may change during that
0.5 seconds if another robot joined the network.

Simple Remotely Controlled Robot
--------------------------------

This example implements a simple control system with two Raspberry Pi's. One
RPi is mounted on a robot, connected to motors with an H-Bridge (the robot), while
the other is connected to only a button (the controller).

The code on the controller is pretty simple

.. literalinclude:: examples/button_control_controller.py

There is nothing fancy in this code. The usage of :func:`~functools.partial` is
to wrap it into a callable, as required by :attr:`~gpiozero.Button.when_pressed`
and :attr:`~gpiozero.Button.when_released` attributes. It is the equivalent of

.. code-block::

    def send_on_wrapper():
        robot.network.send('on',0)

    def send_off_wrapper():
        robot.network.send('off',0)

    button.when_pressed = send_on_wrapper
    button.when_released = send_off_wrapper

This code assumes the ID of the robot is 0. In the case that the ID of the
robot is unknown, you should consider using :meth:`~crh_botnet.network.RobotNetwork.broadcast`.

The code on the robot side looks slightly more complicated, but the most of it
is initializing the H-Bridge. The rest of them should be pretty self-explanatory.

.. literalinclude:: examples/button_controls_drive.py


.. _hbridge:

HBridge Drive
-------------

*Added in version 0.2.0*

A simple code for using :class:`~drive.HBridgeDrive` class.

.. literalinclude:: examples/h_bridge_drive.py

An alternative code (which makes it look more elegant) is

.. literalinclude:: examples/h_bridge_drive_alt.py

As the :meth:`drive.HBridgeDrive.__call__` function is just a convenience wrapper
around :meth:`drive.HBridgeDrive.drive`.
