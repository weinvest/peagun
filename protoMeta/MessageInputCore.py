import sys
import exceptions
from TypeDispatcher import TypeDispatcher
from decorator import decorator


class ValueRangeError(exceptions.Exception):
    def __init__(self, typeName, minValue, maxValue, real):
        super(ValueRangeError, self).__init__()
        self.message = 'value range of %s is [%d,%d],but i see %d' % (typeName, minValue, maxValue, real)

    def __str__(self):
        return repr(self.message)

    @staticmethod
    def checkOrRaise(typeName, minValue, maxValue, real):
        if real >= minValue and real <= maxValue:
            return real
        else:
            raise ValueRangeError(typeName, minValue, maxValue, real)


class EnumValueError(exceptions.Exception):
    def __init__(self, typeName, value):
        self.message = value + ' is not a valid value of enum:' + typeName

    def __str__(self):
        return repr(self.message)


class ControlException(exceptions.Exception):
    pass


class GiveUpField(ControlException):
    pass


class GiveUpMessage(ControlException):
    pass


class NoMoreElements(ControlException):
    pass


class MessageInputer(object):
    def inputValue(self, fieldSpec, fieldName):
        pass

    def inputError(self, exception):
        pass

    def beginList(self, fieldSpec, fieldName):
        pass

    def endList(self, fieldSpec, fieldName):
        pass

    def beginMap(self, fieldSpec, fieldName):
        pass

    def endMap(self, fieldSpec, fieldName):
        pass

    def beginStruct(self, fieldSpec, fieldName):
        pass

    def endStruct(self, fieldSpec, fieldName):
        pass

    def getCompleteList(self):
        return None


class MessageInputCore(TypeDispatcher):
    def __init__(self, inputer):
        super(MessageInputCore, self).__init__('input')
        self.inputer = inputer

    @staticmethod
    def create(spec):
        module = None
        moduleName = spec.moduleName + '.ttypes'
        if spec.moduleName != '' and not sys.modules.has_key(moduleName):
            module = __import__(moduleName)
        else:
            module = sys.modules[spec.moduleName]

        constructor = getattr(module.ttypes, spec.getName())
        if constructor is not None:
            return constructor()

        return None

    @decorator
    def waitGoodValueOrGiveUp(f, self, fieldSpec, fieldName):
        while True:
            try:
                value = f(self, fieldSpec, fieldName)
                return value
            except ControlException, e:
                raise
            except exceptions.Exception, e:
                self.inputer.inputError(e)


    @waitGoodValueOrGiveUp
    def inputBool(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = strValue.lower() in ("yes", "true", "t", "1", "y")
        return value

    @waitGoodValueOrGiveUp
    def inputByte(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = int(strValue)
        return ValueRangeError.checkOrRaise('byte', -128, 127, value)


    @waitGoodValueOrGiveUp
    def inputI16(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = int(strValue)
        return ValueRangeError.checkOrRaise('i16', -1 << 15, (1 << 15) - 1, value)


    @waitGoodValueOrGiveUp
    def inputI32(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = int(strValue)
        return ValueRangeError.checkOrRaise('i32', -1 << 31, (1 << 31) - 1, value)

    @waitGoodValueOrGiveUp
    def inputI64(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = int(strValue)
        return ValueRangeError.checkOrRaise('i64', -1 << 63, (1 << 63) - 1, value)

    @waitGoodValueOrGiveUp
    def inputDouble(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)
        value = float(strValue)
        return value

    @waitGoodValueOrGiveUp
    def inputEnum(self, fieldSpec, fieldName):
        strValue = self.inputer.inputValue(fieldSpec, fieldName)

        if fieldSpec.string2Values.has_key(strValue):
            return fieldSpec.string2Value(strValue)
        else:
            if strValue.startswith('0x') or strValue.startswith('0X'):
                value = int(strValue, 16)
            else:
                value = int(strValue)

            if not fieldSpec.value2Strings.has_key(value):
                raise EnumValueError(fieldSpec.getName(), strValue)
            return value


    @waitGoodValueOrGiveUp
    def inputString(self, fieldSpec, fieldName):
        return self.inputer.inputValue(fieldSpec, fieldName)

    def inputList(self, fieldSpec, fieldName):
        l = []

        self.inputer.beginList(fieldSpec, fieldName)
        seq = 1
        while True:
            try:
                item = self.dispatch(fieldSpec.valueSpec, 'item-%2d' % seq)
                l.append(item)
                seq = seq + 1
            except GiveUpField, g:
                continue
            except NoMoreElements, n:
                break

        self.inputer.endList(fieldSpec, fieldName)
        return l

    def inputMap(self, fieldSpec, fieldName):
        m = {}

        self.inputer.beginMap(fieldSpec, fieldName)
        seq = 1
        while True:
            try:
                key = self.dispatch(fieldSpec.keySpec, 'key-%-2d:' % seq)
                value = self.dispatch(fieldSpec.valueSpec, 'val-%-2d:' % seq)
                m[key] = value
                seq = seq + 1
            except GiveUpField, g:
                continue
            except NoMoreElements, n:
                break

        self.inputer.endMap(fieldSpec, fieldName)
        return m

    def inputStruct(self, spec, fieldName):
        obj = self.create(spec)
        self.inputer.beginStruct(spec, fieldName)
        for fieldName, fieldSpec in spec.fields.items():
            try:
                field = self.dispatch(fieldSpec, fieldName)
            except GiveUpField, g:
                continue
            except NoMoreElements, e:
                self.inputer.endStruct(spec, fieldName)
                raise

            if field is not None:
                setattr(obj, fieldName, field)
        self.inputer.endStruct(spec, fieldName)
        return obj

    def getCompleteList(self):
        return self.inputer.getCompleteList()

    def input(self, spec):
        try:
            return self.dispatch(spec, '')
        except (GiveUpField, GiveUpMessage):
            return None

