from thrift.Thrift import TType
import TypeSpec


class MessageSpec(object):
    def __init__(self, codeName, code):
        self.__codeName = codeName
        self.__messageCode = code
        self.__requestSpec = None
        self.__responseSpec = None
        self.__parseName()

    def __parseName(self):
        nameWords = self.getCodeName().split('_')
        self.__name = ''.join(nameWords[2:])
        self.__name = self.__name.lower()


    def setInitiatorSpec(self, requestSpec):
        self.__requestSpec = requestSpec

    def getInitiatorSpec(self):
        return self.__requestSpec

    def setAcceptorSpec(self, responseSpec):
        self.__responseSpec = responseSpec

    def getAcceptorSpec(self):
        return self.__responseSpec

    def getName(self):
        return self.__name

    def getCode(self):
        return self.__messageCode

    def getCodeName(self):
        return self.__codeName


class MessageSpecDict(object):
    def __init__(self):
        self.nameDict = {}
        self.codeDict = {}
        self.typeDict = {}
        self.__currentModule = ''

        self.addType(TypeSpec.TypeSpec(TType.BOOL, 'bool'))
        self.addType(TypeSpec.TypeSpec(TType.BYTE, 'byte'))
        self.addType(TypeSpec.TypeSpec(TType.DOUBLE, 'double'))
        self.addType(TypeSpec.TypeSpec(TType.I16, 'i16'))
        self.addType(TypeSpec.TypeSpec(TType.I32, 'i32'))
        self.addType(TypeSpec.TypeSpec(TType.I64, 'i64'))
        self.addType(TypeSpec.TypeSpec(TType.STRING, 'string'))

    def setCurrentModule(self, m):
        self.__currentModule = m

    def getCurrentModule(self):
        return self.__currentModule

    def add(self, msgSpec):
        if msgSpec is not None:
            self.nameDict[msgSpec.getName() + ':' + self.__currentModule.lower()] = msgSpec
            self.codeDict[msgSpec.getCode()] = msgSpec

    def addType(self, t):
        t.moduleName = self.__currentModule
        self.typeDict[t.getName() + ':' + self.__currentModule] = t

    def addAlias(self, name, t):
        self.typeDict[name + ':' + self.__currentModule] = t

    def getType(self, name):
        t = self.typeDict.get(name)
        if t is None:
            t = self.typeDict.get(name[:name.rfind(':') + 1])

        return t

    def getTypeEx(self, name):
        t = self.typeDict.get(name)
        if t is None:
            name = name[:name.rfind(':') + 1]
            t = self.typeDict.get(name)

        return name, t

    def getByName(self, name):
        return self.nameDict.get(name.lower())

    def getByCode(self, code):
        return self.codeDict.get(code)


