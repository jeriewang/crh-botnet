The Network Module
==================

.. autoclass:: crh_botnet.network.RobotNetwork
    :members:

    .. attribute:: connected_robots

        A list of IDs of all connected robots. It is not guaranteed to be
        in a particular order. Updates roughly once per 0.2 seconds.

    .. attribute:: coro

        An instance of :class:`AsyncMethodsWrapper`

.. autoclass:: crh_botnet.network.AsyncMethodsWrapper
    :members:
