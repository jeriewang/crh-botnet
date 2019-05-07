The Network Interface
=====================

For convenience, all public methods and attributes of this class are exposed to
the :class:`~crh_botnet.robot.Robot` class. For example

.. code-block::

    from crh_botnet import *
    robot=Robot()

    robot.network.set_server_address("choate-robotics-rpi-01.local") # The "legit" way
    robot.set_server_address("choate-robotics-rpi-01.local") # Also valid

    def setup():
        robot.network.broadcast("Hi") # What is documented

        robot.broadcast("Hi again")
        # Also valid because all methods are exposed to the robot.

        robot.shutdown()

    robot.run(globals())

.. autoclass:: crh_botnet.network.RobotNetwork
    :members:

    .. attribute:: connected_robots

        A list of IDs of all connected robots. It is not guaranteed to be
        in a particular order. Updates roughly once per 0.2 seconds.

    .. attribute:: coro

        An instance of :class:`AsyncMethodsWrapper`

.. autoclass:: crh_botnet.network.AsyncMethodsWrapper
    :members:

