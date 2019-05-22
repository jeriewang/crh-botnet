Introduction
============

This module is the core of the library. It creates a simulation of an arduino
program in that it lets you have a :func:`setup()` and a :func:`loop()`.
It does everything transparently, including scheduling the executions of
:func:`loop()` and checks messages over the network from time to time. It
utilizes Python's newest :mod:`asyncio` feature to ensure
maximum performance.

All you need to do is to wrap your code inside

.. code-block::
    :linenos:

    from crh_botnet import *

    robot=Robot()
    robot.network.set_server_address("choate-robotics-rpi-01.local")
    # You should substitute this with the actual addresses,
    # which should include the port number if necessary

    def setup():
        # your code goes into here

    def loop():
        # your code goes into here
        # you can delete this function if nothing would go inside

    robot.run(globals())

And you are good to go. Don't worry about what the :func:`globals()` is doing
there. It's what it takes (quite literally) to make the magic work.

.. warning::
    Never use :func:`time.sleep` inside your functions! It will break things.
    If you want a delay, use :func:`asyncio.sleep` and read :ref:`async_funcs`.

A few things should be noticed:

#. The ``robot`` variable should be constructed before everything else.
#. Nothing should be placed after :code:`robot.run(globals())`. Well, you could, they just won't be executed.
#. You don't have to put anything into the :func:`loop()` and :func:`setup()` if you don't want to. In fact, they don't have to be defined at all.

Running The Robot
-----------------

When running the robot, you can pass in several options. The most important ones are :code:`offline` and :code:`debug`.

If don't have a server setup, you can ask the robot to run under offline mode.
Of course, in this case, no network related function will work (and you will probably get a bunch of errors if you try to use them).

.. code-block::

    robot.run(globals(), offline=True)

If you ever wonder what's going on in this library, setting :code:`debug` to :code:`True` is probably a good thing to do.

.. code-block::

    robot.run(globals(), debug=True)


Refer to :meth:`robot.Robot.run` for more details.

Collected Functions
===================

.. note::

    This part of the documentation uses the word
    :ref:`coroutine <coroutine>`, coroutine function, and async function
    interchangeably. If you don't know what it is, you can read section
    :ref:`async_funcs` for a quick introduction.

When :meth:`~crh_botnet.robot.Robot.run` is called, the following functions will be collected
(from the namespace passed to run):

- :func:`setup`
- :func:`loop`
- :func:`on_message`
- :func:`on_shutdown`

They default to do nothing if not defined.

.. function:: setup()

    This function will be called exactly once,
    after connecting to the robot network. and before the first execution
    of :func:`loop`. All variables defined inside :func:`setup()`
    will be injected back to the global namespace. Unlike other collected
    functions, this function cannot be a :ref:`coroutine <coroutine>`.

.. function:: loop()

    The collected loop function. It is called once every 50 ms by default.
    You can change the frequency by calling :func:`~Robot.set_looping_interval`.

    If you want to have control over the looping time, or adding custom delay
    here and there, you can mark the loop as asynchronous with the async keyword.
    For example:

    .. code-block::

        c=0

        async def loop():
            global c
            if c % 100 == 0:
                await sleep(0.5)
            c+=1

    You can set the looping_interval to be 0, in that case,
    the loop is called as many times as possible
    (2007584 times per second, tested on a Macbook Pro),
    and it is your responsibility to call :func:`~asyncio.sleep()` if desired.
    For your convenience, the sleep function is imported at the top level of
    :mod:`crh_botnet` and is included when you execute
    :code:`from crh_botnet import *`.

    .. warning::
        Don't forget the :keyword:`await` before :func:`~asyncio.sleep()`.



.. function:: on_message(message)

    This function is called when a new message has arrived. It takes a single
    argument, which is a :class:`message.Message` object. It can be either a
    :ref:`coroutine <coroutine>` function or a regular function.

.. function:: on_shutdown()

    This function is called during the shutdown sequence, before the robot
    disconnects from the network. You can use it to perform some clean up
    or send a last second goodbye message to another beloved robot (which
    you shouldn't have to because they can see if you are offline). It can be
    either a :ref:`coroutine <coroutine>` function or a regular function.

.. _async_funcs:

Async Flavored Functions
========================

All collected functions can be optionally marked as a :ref:`coroutine <coroutine>`
function with the special keyword :keyword:`async` before the function definition.


What Is :code:`await`?
----------------------

When your program hits a line with :keyword:`await`, the control flow of the
program is transferred back to the event loop, which is called a context switch.
This is a fairly complicated concept and is outside of the scope of this
documentation.

For the particular case of :code:`await sleep`, it is basically equivalent to
that your program gives up the control of the CPU for that particular time
period. For example, if you have this function

.. code-block::
    :emphasize-lines: 4

    async def loop():
        # do something

        await sleep(0.05)

        # do something else

Every time the loop hits line 4, it is instructing the Python interpreter that
"I voluntarily give up the control of the CPU for 0.05 seconds, you are free
to do whatever you want for 0.05 seconds." (This is called a voluntary context
switch.) During this 0.05 seconds, the control is transferred back to the event
loop, which is managed by this library. The library will use the time to check
whether a new message has arrived (and if so, invoke the
:func:`on_message` handler) , send out messages scheduled
with :func:`~crh_botnet.network.RobotNetwork.send()`, etc.

If you are still not sure how to use this package, checkout some
:ref:`examples <examples>`.
