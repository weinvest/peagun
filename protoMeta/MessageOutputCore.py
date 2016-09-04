import sys
import exceptions
from TypeDispatcher import TypeDispatcher
from decorator import decorator


class MessageOutputer(object):
    def outputValue(self, fieldSpec, fieldName, obj):
        pass

    def outputError(self, exception):
        pass

    def beginList(self, fieldSpec, fieldName, obj):
        pass

    def endList(self, fieldSpec, fieldName, obj):
        pass

    def beginMap(self, fieldSpec, fieldName, obj):
        pass

    def endMap(self, fieldSpec, fieldName, obj):
        pass

    def beginStruct(self, fieldSpec, fieldName, obj):
        pass

    def endStruct(self, fieldSpec, fieldName, obj):
        pass


class MessageOutputCore(TypeDispatcher):
    def __init__(self, outputer):
        super(MessageOutputCore, self).__init__('output')
        self.outputer = outputer

    def outputBool(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputByte(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputI16(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputI32(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputI64(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputDouble(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputEnum(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputString(self, fieldSpec, fieldName, obj):
        self.outputer.outputValue(fieldSpec, fieldName, obj)

    def outputList(self, fieldSpec, fieldName, obj):
        self.outputer.beginList(fieldSpec, fieldName, obj)
        if obj is not None:
            seq = 1
            for item in obj:
                self.dispatch(fieldSpec.valueSpec, 'item-%2d' % seq, item)
                seq = seq + 1

        self.outputer.endList(fieldSpec, fieldName, obj)

    def outputMap(self, fieldSpec, fieldName, obj):
        self.outputer.beginMap(fieldSpec, fieldName, obj)
        if obj is not None:
            seq = 1
            for (key, val) in obj.items():
                self.dispatch(fieldSpec.keySpec, 'key-%-2d:' % seq, key)
                self.dispatch(fieldSpec.valueSpec, 'val-%-2d:' % seq, val)
                seq = seq + 1

        self.outputer.endMap(fieldSpec, fieldName, obj)

    def outputStruct(self, spec, fieldName, obj):
        self.outputer.beginStruct(spec, fieldName, obj)
        if obj is not None:
            for fieldName, fieldSpec in spec.fields.items():
                self.dispatch(fieldSpec, fieldName, getattr(obj, fieldName))

        self.outputer.endStruct(spec, fieldName, obj)


    def output(self, spec, obj):
        return self.dispatch(spec, '', obj)

