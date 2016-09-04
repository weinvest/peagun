from protoMeta.MessageOutputCore import MessageOutputer
from protoMeta.TypeSpec import EnumSpec

class JsonOutputer(MessageOutputer):
    def __init__(self,sink):
        self.indent = 0
        self.sink = sink
        self.fieldIndex = [0]

    def indentString(self):
        return ' ' * self.indent

    def writeFieldName(self,fieldName):
        if 0 == len(fieldName):
            return
        if fieldName.startswith('val-'):
            self.sink.write(':')
        else:
            if self.fieldIndex[-1] != 0:
                self.sink.write(',\n')
            self.sink.write(self.indentString())
            if not fieldName.startswith('item-') and not fieldName.startswith('key-'):
                self.sink.write('"' + fieldName + '":')

    def writeCompositeBegin(self,fieldName,bracket):
        self.writeFieldName(fieldName)
        self.sink.write('\n' + self.indentString() + bracket + '\n')
        self.indent = self.indent + 4
        self.fieldIndex.append(0)

    def writeCompositeEnd(self,bracket):
        self.indent = self.indent - 4
        self.sink.write('\n' + self.indentString() + bracket)
        self.fieldIndex.pop()
        self.fieldIndex[-1] += 1

    def outputValue(self,fieldSpec,fieldName,obj):
        if isinstance(fieldSpec,EnumSpec):
            obj = fieldSpec.value2String(obj)

        self.writeFieldName(fieldName)
        if fieldName.startswith('key-'):
            self.sink.write('"' + str(obj) + '"')
        else:
            self.sink.write('"' + str(obj) + '"')
            self.fieldIndex[-1] += 1

    def beginStruct(self,fieldSpec,fieldName,obj):
        self.writeCompositeBegin(fieldName,'{')

    def endStruct(self,fieldSpec,fieldName,obj):
        self.writeCompositeEnd('}')

    def beginList(self,fieldSpec,fieldName,obj):
        self.writeCompositeBegin(fieldName,'[')

    def endList(self,fieldSpec,fieldName,obj):
        self.writeCompositeEnd(']')

    def beginMap(self,fieldSpec,fieldName,obj):
        self.writeCompositeBegin(fieldName,'{')

    def endMap(self,fieldSpec,fieldName,obj):
        self.writeCompositeEnd('}')


