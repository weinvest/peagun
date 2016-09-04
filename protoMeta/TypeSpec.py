import re
from thrift.Thrift import TType


class TypeSpec(object):
    suffixPattern = re.compile('(.+)([A-Z][a-z0-9_]+)')

    def __init__(self, typeCode, name):
        self.typeCode = typeCode
        self.name = name
        self.moduleName = ''
        self.messageName = ''
        self.messageTypeCode = -1
        self.roleValue = 0  # 0--unknown 1--initiator 2--acceptor
        self._assignRole()

    def _assignRole(self):
        m = self.suffixPattern.match(self.name)
        if m is not None:
            suffix = m.group(2)
            from network.WMessage import WMessageType

            if WMessageType.name2Values.has_key(suffix):
                isInitiator = WMessageType.isInitiator(WMessageType.name2Values[suffix])
                self.messageTypeCode = WMessageType.name2Values[suffix]
                if isInitiator:
                    self.roleValue = 1
                    self.messageName = m.group(1).lower()
                else:
                    self.roleValue = 2
                    self.messageName = m.group(1).lower()

    def getModuleName(self):
        return self.moduleName

    def getMessageName(self):
        if -1 == self.messageName.find(':') and 0 != len(self.moduleName):
            self.messageName += ':' + self.moduleName.lower()
        return self.messageName

    def getMessageTypeCode(self):
        return self.messageTypeCode

    def getTypeCode(self):
        return self.typeCode

    def getName(self):
        return self.name

    def isInitiator(self):
        return 1 == self.roleValue

    def isAcceptor(self):
        return 2 == self.roleValue

    def getTypeName(self):
        return TType._VALUES_TO_NAMES[self.getTypeCode()].capitalize()


class EnumSpec(TypeSpec):
    def __init__(self, name):
        TypeSpec.__init__(self, TType.I32, name)
        self.value2Strings = {}
        self.string2Values = {}

    def addValue(self, name, value):
        self.string2Values[name] = value
        self.value2Strings[value] = name

    def value2String(self, v):
        return self.value2Strings[v]

    def string2Value(self, s):
        return self.string2Values[s]

    def getTypeName(self):
        return 'Enum'


class StructSpec(TypeSpec):
    def __init__(self, name):
        TypeSpec.__init__(self, TType.STRUCT, name)
        self.fields = {}

    def addField(self, fieldName, typeSpec):
        self.fields[fieldName] = typeSpec


class ListSpec(TypeSpec):
    def __init__(self, name, valueSpec):
        TypeSpec.__init__(self, TType.LIST, name)
        self.valueSpec = valueSpec


class MapSpec(TypeSpec):
    def __init__(self, name, keySpec, valueSpec):
        TypeSpec.__init__(self, TType.MAP, name)
        self.keySpec = keySpec;
        self.valueSpec = valueSpec

