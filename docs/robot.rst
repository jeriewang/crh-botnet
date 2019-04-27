The Robot Module
================

.. autoclass:: crh_botnet.Robot
    :members:
    :exclude-members: network, id

    .. attribute:: network

        An instance of :class:`~crh_botnet.network.RobotNetwork`.

    .. attribute:: id

        The robot's ID. int. It is None until :meth:`run` is called.
