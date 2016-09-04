import sys
from exceptions import KeyboardInterrupt
from exceptions import EOFError
from protoMeta.MessageInputCore import MessageInputer
from protoMeta.MessageInputCore import GiveUpField
from protoMeta.MessageInputCore import GiveUpMessage
from protoMeta.MessageInputCore import NoMoreElements
from termcolor import colored, cprint
from protoMeta.TypeSpec import EnumSpec

class ControlInputer(MessageInputer):
    def __init__(self):
        self.indent = 0
        self.giveUpStreak = False
        self.inputSpec = None
    def inputValue(self,fieldSpec,fieldName):
        try:
            self.inputSpec = fieldSpec
            strValue = raw_input(self.indentString() + fieldName + '(' + fieldSpec.getName() + '):')
            if self.giveUpStreak and strValue == '\q':
                raise NoMoreElements()
            elif strValue.startswith('@'):
                f = open(strValue[1:],'r')
                strValue = ''.join(f.readlines())

            return strValue
        except KeyboardInterrupt:
            raise GiveUpField()
        except EOFError:
            self.indent = 0
            raise GiveUpMessage()
        finally:
            self.inputSpec = None

    def getCompleteList(self):
        if self.inputSpec is None:
            return None

        if isinstance(self.inputSpec,EnumSpec):
            return self.inputSpec.string2Values.keys()
        else:
            return []

    def indentString(self):
        return ' ' * self.indent
    def inputError(self,ex):
        cprint(self.indentString() + 'exception:' +  ex.message,'red',attrs=['bold'],file=sys.stderr)

    def beginStruct(self,fieldSpec,fieldName):
        if '' != fieldName:
            print(self.indentString() + fieldName + '(' + fieldSpec.getName() + ')')
        self.indent = self.indent + 4

    def endStruct(self,fieldSpec,fieldName):
        self.indent = self.indent - 4

    def beginList(self,fieldSpec,fieldName):
        print(self.indentString() + fieldName + '(list)')
        self.indent = self.indent + 4
        self.giveUpStreak = True

    def endList(self,fieldSpec,fieldName):
        self.indent = self.indent - 4
        self.giveUpStreak = False

    def beginMap(self,fieldSpec,fieldName):
        print(self.indentString() + fieldName + '(map)')
        self.giveUpStreak = True
        self.indent = self.indent + 4


    def endMap(self,fieldSpec,fieldName):
        self.indent = self.indent - 4
        self.giveUpStreak = False



