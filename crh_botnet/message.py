import time, json,datetime


class Message:
    """
    This class contains the implementation of a message that a robot sends.
    """
    
    __slots__ = ['content', 'sender', 'time_created', 'recipient']
    
    def __init__(self, msg: str):
        """
        :param msg: A string for sending. It is set to be the message's content.
        """
        self.content = msg
        "The message content, :class:`str`"
        
        self.sender = None
        "ID of the message sender, :class:`int`"
        
        self.time_created = datetime.datetime.now()
        "Creation time of the message. :class:`datetime.datetime`. "
        
        self.recipient = None
        "ID of the recipient of the message, :class:`int`"
    
    def set_sender(self, sender):
        """
        :param int sender: The sender's id
        :return: None
        """
        self.sender = sender
    
    def set_recipient(self, recipient):
        """
        :param int recipient: The recipient's ID or special value -1 indicating\
        that the message should be broadcast.
        :return: None
        """
        self.recipient = recipient
    
    @classmethod
    def from_json(cls, msg: str):
        """
        :param str msg: A JSON serialized message.
        :return: The message.
        :rtype: Message
        """
        
        obj = json.loads(msg)
        msg = Message(str(obj['content']))
        msg.set_recipient(int(obj['recipient']))
        msg.set_sender(int(obj['sender']))
        msg.time_created = datetime.datetime.utcfromtimestamp(float(obj['time_created']))
        return msg
    
    @classmethod
    def from_dict(cls, d: dict):
        """
        :param dict d: The message
        :return: The message.
        :rtype: Message
        """
    
        msg = Message(str(d['content']))
        msg.set_recipient(int(d['recipient']))
        msg.set_sender(int(d['sender']))
        msg.time_created = datetime.datetime.utcfromtimestamp(float(d['time_created']))
        return msg

    @classmethod
    def from_db_record(cls, record):
        """
        :param record: A message retrieved from db.
        :type record: sqlite3.Row
        :return: The message.
        :rtype: Message
        """
        
        msg=cls(record['content'])
        msg.set_sender(record['sender'])
        msg.set_recipient(record['recipient'])
        msg.time_created=record['time_created']
        
        return msg
        
    
    def to_json(self):
        """
        :return: The JSON serialization of the message.
        :rtype: str
        """
        if self.recipient is None:
            raise ValueError('Message recipient cannot be None')
        if self.sender is None:
            raise ValueError('Message sender cannot be None')
        
        return json.dumps({
            'content'     : self.content,
            'sender'      : self.sender,
            'recipient'   : self.recipient,
            'time_created': self.time_created.timestamp()
        })

    def to_dict(self):
        """
        :return: The message as a JSON serializable dict.
        :rtype: dict
        """
        if self.recipient is None:
            raise ValueError('Message recipient cannot be None')
        if self.sender is None:
            raise ValueError('Message sender cannot be None')
    
        return {
            'content'     : self.content,
            'sender'      : self.sender,
            'recipient'   : self.recipient,
            'time_created': self.time_created.timestamp()
        }
    
    
    def validate(self):
        """
        Check if the message is valid.
        
        :rtype: bool
        """
        return self.recipient is not None and self.sender is not None
    
    def __eq__(self, other):
        if not isinstance(other, Message):
            raise TypeError("A message cannot be compared with a %s" % type(other))
        
        return self.content == other.content and \
               self.sender == other.sender and \
               self.time_created == other.time_created and\
               self.recipient == other.recipient
    
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f'<Message from {self.sender} to {self.recipient} "{self.content}">'
