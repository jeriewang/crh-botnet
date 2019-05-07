import asyncio, aiohttp, sys, requests, re
from .message import Message
from typing import Union, List
from types import FunctionType


class RobotNetwork:
    """
    The networking interface that enable robots to communicate with each other.
    It provides functionalities for a robot to send a message to another robot,
    or to broadcast a message to every single robot in the network.
    """
    
    SERVER_ADDR = 'http://localhost:5003'
    
    def __init__(self, robot):
        """
        :param crh_botnet.robot.Robot robot: The robot.
        """
        self._robot = robot
        self._is_connected = asyncio.Event()
        self.coro = AsyncMethodsWrapper(self)
        self.connected_robots = []
        self.token = None
    
    @property
    def is_connected(self):
        """
        :return: Whether the robot is connected to the network
        :rtype: bool
        """
        return self._is_connected.is_set()
    
    def connect(self):
        """
        Connects to the network.
        
        :return: None
        """
        
        # This function cannot be async because it is called before the event
        # loop is running.
        r = requests.post(f'{self.SERVER_ADDR}/api/connect', json={'id': self._robot.id})
        r.raise_for_status()
        self.token = r.json()['token']
        # print(self.token)
        self._is_connected.set()
    
    def send(self, msg, recipient, callback=None):
        """
        Schedule a message to be sent. Note that this does not send
        out the message immediately. Rather, the message will be sent
        when the event loop is idle (while awaiting something).
        
        :param  msg: The message for sending
        :type msg: str or Message
        :param int recipient: The ID of the recipient.
        :param callback: A callback function that takes a single argument: the \
        :class:`Message` object sent. Defaults to None.
        :type callback: FunctionType or None
        :return: None
        """
        
        fut = asyncio.run_coroutine_threadsafe(self.coro.send(msg, recipient), self._robot._event_loop)
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
    
    def broadcast(self, msg):
        """
        Broadcast a message to the entire robot network.
        
        :param msg: A message
        :type msg: str or Message
        :return: None
        """
        asyncio.run_coroutine_threadsafe(self.coro.broadcast(msg), self._robot._event_loop)
    
    def disconnect(self):
        """
        Disconnect from the network
        :return:
        """
        r = requests.post(f'{self.SERVER_ADDR}/api/disconnect', headers={'Authorization': 'Token ' + self.token})
        r.raise_for_status()
    
    @classmethod
    def set_server_address(cls, address):
        """
        Set the address to the central server. The address is in
        format ``proto://addr:port``.
        The protocol is assumed to be http if left blank.
        
        :param str address: The address of the central server.
        :return: None
        """
        if re.match(r'https?://.+', address):
            cls.SERVER_ADDR = address
        else:
            cls.SERVER_ADDR = 'http://' + address


class AsyncMethodsWrapper:
    """
    This class exists purely for the purpose of scoping. All methods defined
    in this class are :ref:`coroutines <coroutine>`.
    """
    
    def __init__(self, network):
        """
        :param RobotNetwork network: The network
        """
        self._network = network
        self._session = None
    
    async def poll(self) -> List[Message]:
        """
        This function is a a coroutine.

        :return: A list of messages.
        :rtype: list[Message]
        """
        if not self._session:
            await self._create_session()
        
        res = await self._session.get(self._network.SERVER_ADDR + '/api/poll')
        obj = await res.json()
        self._network.connected_robots = obj['robots']
        ret = []
        for m in obj['messages']:
            ret.append(Message.from_dict(m))
        return ret
    
    async def send(self, msg: Message, recipient: int):
        """
        This function is a a coroutine.

        :param msg: The message for sending
        :type msg: Message or str
        :param int recipient: The ID of the recipient.
        :return: The message sent (for callback purpose)
        :rtype: Message
        """
        if not self._session:
            await self._create_session()
        
        if isinstance(msg, str):
            msg = Message(msg)
        assert isinstance(msg, Message)
        msg.set_recipient(recipient)
        msg.set_sender(self._network._robot.id)
        await self._session.put(self._network.SERVER_ADDR + '/api/send', json=msg.to_dict())
        return msg
    
    async def broadcast(self, msg):
        """
        This function is a a coroutine. Broadcast a message to the entire robot network
        :param msg: The message for broadcasting
        :type msg: Message or str
        :return: The message object broadcast (for callback purpose)
        :rtype: Message
        """
        if not self._session:
            await self._create_session()
        
        if isinstance(msg, str):
            msg = Message(msg)
        assert isinstance(msg, Message)
        msg.set_recipient(-1)
        msg.set_sender(self._network._robot.id)
        await self._session.put(self._network.SERVER_ADDR + '/api/send', json=msg.to_dict())
        return msg
    
    async def disconnect(self):
        """
        This function is a a coroutine. Disconnect from the network.

        :return: None
        """
        if not self._session:
            await self._create_session()
        await self._session.post(self._network.SERVER_ADDR + '/api/disconnect')
    
    async def retrieve(self, msg_id: int):
        """
        This function is a coroutine.

        :param int msg_id: The message id
        :return: The retrieved message
        :rtype: Message
        """
        if not self._session:
            await self._create_session()
        
        raise NotImplementedError
    
    async def _create_session(self):
        if not self._network.is_connected:
            raise ConnectionError('The RobotNetwork is not connected')
        self._session = aiohttp.ClientSession(
                raise_for_status=True,
                headers={'Authorization': 'Token ' + self._network.token}
        )
