.. _examples:

Examples
========

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
