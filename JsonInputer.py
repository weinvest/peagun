import sys
from exceptions import KeyboardInterrupt
from exceptions import EOFError
from protoMeta.MessageInputCore import MessageInputer
from protoMeta.MessageInputCore import GiveUpField
from protoMeta.MessageInputCore import GiveUpMessage
from protoMeta.MessageInputCore import NoMoreElements
from termcolor import colored, cprint
from protoMeta.TypeSpec import EnumSpec

class JsonInputer(MessageInputer):
    def __init__(self,jsonObject):
        self.jsonObject = jsonObject
        self.inputStack = []
        self.generators = []

    def getField(self,fieldName):
        if fieldName.startswith('key-') or fieldName.startswith('val-') or fieldName.startswith('item-'):
            return self.generators[-1].next()
        elif self.inputStack[-1].has_key(fieldName):
            return self.inputStack[-1][fieldName]
        else:
            raise GiveUpField()

    def getMapField(self,fieldName):
        for (key,val) in self.inputStack[-1].items():
            yield key
            yield val
        raise NoMoreElements()

    def getListField(self,fieldName):
        for item in self.inputStack[-1]:
            yield item

        raise NoMoreElements()


    def push(self,fieldName):
        if '' == fieldName:
            self.inputStack.append(self.jsonObject)
        else:
            self.inputStack.append(self.getField(fieldName))

    def pop(self):
        self.inputStack.pop()

    def inputValue(self,fieldSpec,fieldName):
        return self.getField(fieldName)

    def inputError(self,ex):
        cprint('exception:' +  ex.message,'red',attrs=['bold'],file=sys.stderr)

    def beginStruct(self,fieldSpec,fieldName):
        self.push(fieldName)

    def endStruct(self,fieldSpec,fieldName):
        self.pop()

    def beginList(self,fieldSpec,fieldName):
        self.push(fieldName)
        self.generators.append(self.getListField(fieldName))

    def endList(self,fieldSpec,fieldName):
        self.pop()
        self.generators.pop()

    def beginMap(self,fieldSpec,fieldName):
        self.push(fieldName)
        self.generators.append(self.getMapField(fieldName))

    def endMap(self,fieldSpec,fieldName):
        self.pop()
        self.generators.pop()



