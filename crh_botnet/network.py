import asyncio, aiohttp, sys
from .message import Message
from typing import Union, List
from types import FunctionType


class AsyncMethodsWrapper:
    def __init__(self, network):
        """
        :param RobotNetwork robot: The network
        """
        self._network = network

    async def connect(self):
        """
        This function is a coroutine. Connects to the network.
        :return: None
        """

    async def poll(self) -> List[int]:
        """
        This function is a a coroutine.

        :return: A list of message IDs.
        :rtype: list[int]
        """
        raise NotImplementedError

    async def send(self, msg: Message, recipient: int):
        """
        This function is a a coroutine.

        :param Message msg: The message for sending
        :param int recipient: The ID of the recipient.
        :return: The message sent (for callback purpose)
        :rtype: Message
        """
        raise NotImplementedError
    
    async def broadcast(self, msg: Message):
        """
        This function is a a coroutine. Broadcast a message to the entire robot network
        :param Message msg: The message for broadcasting
        :return: The message object broadcast (for callback purpose)
        :rtype: Message
        """

    async def disconnect(self):
        """
        This function is a a coroutine. Disconnect from the network.

        :return: None
        """
        raise NotImplementedError

    async def retrieve(self, msg_id: int):
        """
        This function is a coroutine.

        :param int msg_id: The message id
        :return: The retrieved message
        :rtype: Message
        """
        raise NotImplementedError


    async def get_connected_robots(self):
        """
        This function is a coroutine. Get all robots that are currently connected
        to the network.
        :return: A list of robot IDs.
        :rtype: list[int]
        """
    
    
class RobotNetwork:
    """
    The networking interface that enable robots to communicate with each other.
    It provides functionalities for a robot to send a message to another robot,
    or to broadcast a message to every single robot in the network.
    """
    
    SERVER_ADDR='localhost:5001'
    
    def __init__(self, robot):
        """
        :param crh_botnet.robot.Robot robot: The robot.
        """
        self._robot = robot
        self._is_connected = asyncio.Event()
        self.coro=AsyncMethodsWrapper(self)
        self.connected_robots=[]
    
    @property
    def is_connected(self):
        return self._is_connected.is_set()

    def connect(self):
        """
        Connects to the network.
        
        :return: None
        """
    
    
    def send(self, msg: Message, recipient: int, callback=None):
        """
        Schedule a message to be sent. Note that this does not send
        out the message immediately. Rather, the message will be sent
        when the event loop is idle (while awaiting something).
        
        :param Message msg: The message for sending
        :param int recipient: The ID of the recipient.
        :param callback: A callback function that takes a single argument: the \
        :class:`Message` object sent. Defaults to None.
        :type callback: FunctionType or None
        :return: None
        """
        
        fut = asyncio.ensure_future(self.coro.send(msg, recipient))
        if callback is not None:
            def cb(fut):
                try:
                    res = fut.result()
                except Exception:
                    print(f'Sending message {msg} failed with exception {Exception}. Retrying...', file=sys.stderr)
                    self.send(msg, recipient)  # Try again
                    return
                
                callback(res)
        else:
            def cb(fut):
                try:
                    fut.result()
                except Exception:
                    print(f'Sending message {msg} failed with exception {Exception}. Retrying...', file=sys.stderr)
                    self.send(msg, recipient)  # Try again
        
        fut.add_done_callback(cb)
    

    def broadcast(self, msg: Message):
        """
        Broadcast a message to the entire robot network.
        
        :param msg: A :class:`Message` object for broadcasting
        :return: None
        """
        asyncio.ensure_future(self.broadcast(msg))
    
    
    def disconnect(self):
        """
        Disconnect from the network
        :return:
        """


    @classmethod
    def set_server_address(cls, addr):
        """
        :param str addr: The address of the central server.
        :return: None
        """
    
        cls.SERVER_ADDR = addr

