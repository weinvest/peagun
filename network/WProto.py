from twisted.internet import reactor, protocol
from WMessage import WMessage
from WSignal import WSignal


class DispatchItem(object):
    def __init__(self, t, handle):
        self.Type = t
        self.Handle = handle


class WProto(protocol.Protocol):
    def __init__(self):
        self.__data = ''
        self.__message = None
        self.onConnected = WSignal()
        self.onClosed = WSignal()
        self.dispatchDict = {}

    def connectionMade(self):
        self.onConnected(self)

    def connectionLost(self, reason):
        self.onClosed(self, reason)

    def dataReceived(self, data):
        self.__data += data

        length = len(self.__data)
        if length >= WMessage.getHeaderLength() and self.__message is None:
            self.__message = WMessage()
            self.__message.setHeader(self.__data[0:12])

        if self.__message is not None and length >= self.__message.getLength():
            mesgLen = self.__message.getLength()
            self.__message.setBody(self.__data[12:mesgLen])
            self.__data = self.__data[mesgLen:]
            self._dispatch()

    def send(self, sessionId, itype, request=None):
        message = WMessage.serialize(itype, sessionId, request)
        self.transport.write(message.getHeader() + message.getBody())

    def _dispatch(self):
        iType = self.__message.getType()
        dispatchItem = self.dispatchDict.get(iType, None)
        if dispatchItem is not None:
            obj = dispatchItem.Type()
            obj = self.__message.deserialize(obj)
            dispatchItem.Handle(self._message.getPeer(), obj)

        else:
            self.default(self.__message)

        self.__message = None

    def default(self, msg):
        pass



    
