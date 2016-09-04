from thrift.protocol import TCompactProtocol;
from thrift.transport import TTransport;
from exceptions import Exception
import struct


class WMessageType(object):
    Request = 0
    Response = 1
    Subscribe = 2
    Notify = 4

    value2Names = {Request: 'Request'
        , Response: 'Response'
        , Subscribe: 'Subscribe'
        , Notify: 'Notify'}

    name2Values = {'Request': Request
        , 'Response': Response
        , 'Subscribe': Subscribe
        , 'Notify': Notify}

    @classmethod
    def makeCode(cls, msgType, code):
        return code | (msgType << 24)

    @classmethod
    def parseCode(cls, code):
        msgType = code >> 24
        return (msgType, code & (~(7 << 24)))

    @classmethod
    def isInitiator(cls, msgType):
        return msgType % 2 == 0

    @classmethod
    def isAcceptor(cls, msgType):
        return not cls.isInitiator(msgType)


class WMessage(object):
    def __init__(self):
        self.__length = 12
        self.__type = 0
        self.__peer = 0
        self.__body = None

    def isValid(self):
        return self.getType() != 0

    def getTypeCode(self):
        return WMessageType.parseCode(self.getType())[1]

    def getMessageType(self):
        return WMessageType.parseCode(self.getType())[0]

    def isInitiator(self):
        return WMessageType.isInitiator(self.getMessageType())

    def isAcceptor(self):
        return not self.isInitiator()

    @classmethod
    def getHeaderLength(self):
        return 12

    def getBodyLength(self):
        if self.__body is None:
            return 0
        else:
            return len(self.__body)

    def getType(self):
        return self.__type

    def setType(self, itype):
        self.__type = itype

    def getPeer(self):
        return self.__peer

    def getLength(self):
        return self.__length

    def setPeer(self, peer):
        self.__peer = peer

    def getHeader(self):
        return struct.pack('!III', self.__length, self.__type, self.__peer)

    def setHeader(self, header):
        if len(header) != self.getHeaderLength():
            return
        self.__length, self.__type, self.__peer = struct.unpack('!III', header)

    def getBody(self):
        return self.__body

    def setBody(self, body):
        self.__body = body
        self.__length = self.getHeaderLength() + self.getBodyLength()

    @staticmethod
    def serialize(itype, peer, bodyObj=None):
        message = WMessage()
        message.setType(itype)
        message.setPeer(peer)
        if bodyObj is not None:
            memBuffer = TTransport.TMemoryBuffer()
            protocol = TCompactProtocol.TCompactProtocol(memBuffer)
            bodyObj.write(protocol)
            message.setBody(memBuffer.getvalue())

        return message


    def deserialize(self, obj):
        if self.__body is None or obj is None:
            return None

        try:
            memBuffer = TTransport.TMemoryBuffer(self.__body)
            protocol = TCompactProtocol.TCompactProtocol(memBuffer)
            obj.read(protocol)
        except Exception, e:
            print e.message
            return obj

        return obj 

