from protoMeta.MessageOutputCore import MessageOutputer
from protoMeta.TypeSpec import EnumSpec
class ControlOutputer(MessageOutputer):
    def __init__(self,sink):
        self.indent = 0
        self.sink = sink

    def indentString(self):
        return ' ' * self.indent

    def writeLine(self,text):
        self.sink.write(text + '\n')

    def outputValue(self,fieldSpec,fieldName,obj):
        if isinstance(fieldSpec,EnumSpec):
            obj = fieldSpec.value2String(obj)

        self.writeLine(self.indentString() + fieldName + '(' + fieldSpec.getName() + '):' + str(obj))

    def beginStruct(self,fieldSpec,fieldName,obj):
        if '' != fieldName:
            self.writeLine(self.indentString() + fieldName + '(' + fieldSpec.getName() + ')')
        self.indent = self.indent + 4

    def endStruct(self,fieldSpec,fieldName,obj):
        self.indent = self.indent - 4

    def beginList(self,fieldSpec,fieldName,obj):
        self.writeLine(self.indentString() + fieldName + '(list)')
        self.indent = self.indent + 4

    def endList(self,fieldSpec,fieldName,obj):
        self.indent = self.indent - 4

    def beginMap(self,fieldSpec,fieldName,obj):
        self.writeLine(self.indentString() + fieldName + '(map)')
        self.indent = self.indent + 4


    def endMap(self,fieldSpec,fieldName,obj):
        self.indent = self.indent - 4


