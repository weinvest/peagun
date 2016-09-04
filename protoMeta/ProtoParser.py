import os
import re
import copy
import MessageSpec
import StateMachine
import TypeSpec
import exceptions

class ParseUtil(object):
    listRegex = re.compile(r'(?:list|set)\s*<\s*(\S+)\s*>')
    mapRegex = re.compile(r'map\s*<\s*(\S+)\s*,\s*(\S+)\s*>')

    @classmethod
    def parseTypeName(cls,s,msgSpec):
        module = msgSpec.getCurrentModule()
        dotIndex = s.find('.') 
        if -1 != dotIndex:
            module,s = s[:dotIndex],s[dotIndex + 1:]

        return s + ':' + module


    @classmethod
    def getType(cls,s,msgSpec):
        s = s.strip()
        m = cls.listRegex.match(s)
        if m is not None:
            #list
            valueSpecName = cls.parseTypeName(m.group(1),msgSpec)
            valueSpecName,valueSpec = msgSpec.getTypeEx(valueSpecName)
            if valueSpec is None:
                return None

            name = 'list_' + valueSpecName
            t = msgSpec.getType(name)
            if t is None:
                t = TypeSpec.ListSpec(name,valueSpec)
            msgSpec.addType(t)
            return t
        else:
            m = cls.mapRegex.match(s)
            if m is not None:
                #map
                keyName = cls.parseTypeName(m.group(1),msgSpec)
                valueName = cls.parseTypeName(m.group(2),msgSpec)

                keyName,keySpec = msgSpec.getTypeEx(keyName)
                valueName,valueSpec = msgSpec.getTypeEx(valueName)

                if keySpec is None or valueSpec is None:
                    return None

                name = 'map_' + keyName + '_' + valueName
                t = msgSpec.getType(name)
                if t is None:
                    t = TypeSpec.MapSpec(name,keySpec,valueSpec)
                    msgSpec.addType(t)

                return t
            else:
                #other
                typeName = cls.parseTypeName(s,msgSpec)
                typeSpec = msgSpec.getType(typeName)
                return typeSpec
            
class CannotFindType(exceptions.Exception):
    def __init__(self,t):
        self.typeName = t

    def __str__(self):
        return repr(self.typeName)

class TooManyInitiator(exceptions.Exception):
    def __init__(self,msg):
        self.wmessage = msg

    def __str__(self):
        return repr(self.wmessage)

class TooManyAcceptor(exceptions.Exception):
    def __init__(self,msg):
        self.wmessage = msg

    def __str__(self):
        return repr(self.wmessage)

class LineEvent(object):
    def __init__(self):
        self.line = ''

    def __call__(self,line):
        self.line = line
        return self

class EnumState(StateMachine.StateBase):
    enumMatch = None
    enumRegex = re.compile('enum\s+(\w+)')
    enumValueRegex = re.compile('(\w+)(?:\s*=\s*(0[xX][0-9a-fA-F]+|\d+))?')

    @classmethod
    def isEnumStart(cls,lineEvent):
        cls.enumMatch = cls.enumRegex.match(lineEvent.line)
        return cls.enumMatch is not None

    @classmethod
    def isEnumEnd(cls,lineEvent):
        return lineEvent.line[0] == '}'

    def __init__(self):
        self.__messageSpecDict = {}
    
    def setMessageSpecDict(self,msgSpec):
        self.__messageSpecDict = msgSpec

    def entry(self,evt):
        self.spec = TypeSpec.EnumSpec(self.enumMatch.group(1))
        self.lastValue = 0

    def do(self,evt):
        if evt.line[0] == '{':
            return

        valueMatch = self.enumValueRegex.match(evt.line)
        if valueMatch is None:
            syntaxError = exceptions.SyntaxError()
            syntaxError.message = 'encounter syntax error when parse enum %s ,line %s' % (self.spec.getName(),evt.line)
            raise syntaxError

        enumValue = valueMatch.group(2)
        if enumValue is not None:
            if enumValue.startswith('0x') or enumValue.startswith('0X'):
                self.lastValue = int(enumValue,16)
            else:
                self.lastValue = int(enumValue)

        self.spec.addValue(valueMatch.group(1),self.lastValue)
        self.lastValue = self.lastValue + 1

    def exit(self,evt):
        self.__messageSpecDict.addType(self.spec)

class StructState(StateMachine.StateBase):
    structMatch = None
    structRegex = re.compile('struct\s+(\w+)')
    structFieldRegex = re.compile('\d+\s*:\s*(?:optional\s+|required\s+)?(.+)\s+(\w+)\s*(?:=\s*(\w+)\s*)?;')

    @classmethod
    def isStructStart(cls,lineEvent):
        cls.structMatch = cls.structRegex.match(lineEvent.line)
        return cls.structMatch is not None

    @classmethod
    def isStructEnd(cls,lineEvent):
        return lineEvent.line[0] == '}'

    def __init__(self):
        self.__messageSpecDict = ''

    def setMessageSpecDict(self,msgSpec):
        self.__messageSpecDict = msgSpec

    def entry(self,evt):
        self.spec = TypeSpec.StructSpec(self.structMatch.group(1))

    def exit(self,evt):
        self.__messageSpecDict.addType(self.spec)

    def do(self,evt):
        if evt.line[0] == '{':
            return

        fieldMatch = self.structFieldRegex.match(evt.line)
        if fieldMatch is None:
            syntaxError = exceptions.SyntaxError()
            syntaxError.message = 'encounter syntax error when parse struct %s ,line %s' % (self.spec.getName(),evt.line)
            raise syntaxError
        else:
            typeName = fieldMatch.group(1)
            fieldType = ParseUtil.getType(typeName,self.__messageSpecDict)
            if fieldType is None:
                raise CannotFindType(typeName + ' when parse ' + self.spec.getName())

            self.spec.addField(fieldMatch.group(2),fieldType)



class TypedefState(StateMachine.StateBase):
    typedefRegex = re.compile(r'typedef\s+(\S+)\s+(\w+)')
    typedefMatch = None
    def __init__(self):
        self.__messageSpecDict = None

    @classmethod
    def isTypedef(cls,lineEvent):
        cls.typedefMatch = cls.typedefRegex.match(lineEvent.line)
        return cls.typedefMatch is not None;

    def setMessageSpecDict(self,msgSpecDict):
        self.__messageSpecDict = msgSpecDict

    def entry(self,evt):
        typeName = self.typedefMatch.group(1)
        fromSpec = ParseUtil.getType(typeName,self.__messageSpecDict)
        if fromSpec is None:
            raise CannotFindType(typeName + ' when parse ' + evt.line)

        self.__messageSpecDict.addAlias(self.typedefMatch.group(2),fromSpec)

    def do(self,evt):
        self.entry(evt)
        self.exit(evt)


class MessageState(StateMachine.StateMachine):
    messageCodeRegex = re.compile('const\s+i32\s+([A-Z_0-9]+)\s*=\s*(\d+)')
    messageCodeMatch = None

    def __init__(self,transitions,currentState):
        super(MessageState,self).__init__(transitions,currentState,self.__onStateChanged)
        self.__messageSpecDict = None

    def __onStateChanged(self,fromState,toState):
        if isinstance(fromState,StructState):
            if fromState.spec.isInitiator():
                if self.spec.getInitiatorSpec() is None:
                    self.spec.setInitiatorSpec(fromState.spec)
                else:
                    raise TooManyInitiator(self.spec.getName())
            elif fromState.spec.isAcceptor():
                if self.spec.getAcceptorSpec() is None:
                    self.spec.setAcceptorSpec(fromState.spec)
                else:
                    raise TooManyAcceptor(self.spec.getName())

    @classmethod
    def isMessageCode(cls,evt):
        cls.messageCodeMatch = cls.messageCodeRegex.match(evt.line)
        return cls.messageCodeMatch is not None

    def setMessageSpecDict(self,msgSpecDict):
        self.__messageSpecDict = msgSpecDict

    def entry(self,evt):
        self.spec = MessageSpec.MessageSpec(self.messageCodeMatch.group(1),int(self.messageCodeMatch.group(2)))

    def exit(self,evt):
        self.__messageSpecDict.add(self.spec)

class ProtoParser(object):
    def __init__(self):
        self.__commentsRegex = re.compile('//')
        #events
        self.lineEvent = LineEvent()
        self.eofEvent = LineEvent()

        #states
        self.initState = StateMachine.StateBase()
        self.enumState = EnumState()
        self.structState = StructState()
        self.typedefState = TypedefState()

        #message statemachine
        commonTransitions =  [(self.initState   ,self.lineEvent,  self.structState , StructState.isStructStart  ,None)
                             ,(self.initState   ,self.lineEvent,  self.enumState   , EnumState.isEnumStart      ,None)
                             ,(self.initState   ,self.lineEvent,  self.initState   , TypedefState.isTypedef     ,self.typedefState.do)
                             ,(self.structState ,self.lineEvent,  self.initState   , StructState.isStructEnd    ,None)
                             ,(self.enumState   ,self.lineEvent,  self.initState   , EnumState.isEnumEnd        ,None)
                            ]
        self.messageState = MessageState(commonTransitions,self.initState)

        #main statemachine
        mainTransitions = [(self.initState   ,self.lineEvent  ,self.messageState, MessageState.isMessageCode ,None)
                          ,(self.messageState,self.lineEvent  ,self.messageState, MessageState.isMessageCode ,None)
                          ,(self.messageState,self.eofEvent   ,self.initState   , None                       ,None)
                          ]
        mainTransitions.extend(commonTransitions)
        self.mainStateMachine = StateMachine.StateMachine(mainTransitions,self.initState)

    def parse(self,path,specDict):
        if not os.path.exists(path):
            print('%s not exists' % path)
            return

        if specDict is None:
            print('param ProtoParser.parse.specDict cannot be None')
            return 

        self.enumState.setMessageSpecDict(specDict)
        self.structState.setMessageSpecDict(specDict)
        self.typedefState.setMessageSpecDict(specDict)
        self.messageState.setMessageSpecDict(specDict)

        modules = os.listdir(path)
        modules = self.____topologicSortModules(path,modules)
        for fileName in modules:
            stem,ext = os.path.splitext(fileName)
            if ext == '.thrift':
                specDict.setCurrentModule(stem)
                msgSpec = self.__parseModule(os.path.join(path,fileName),stem)
                specDict.add(msgSpec)


    def __validLine(self,line):
        return self.__commentsRegex.match(line) is None

    def __parseModule(self,path,module):
        protoFile = open(path,'r')
        for line in protoFile:
            line = line.strip()
            if 0 != len(line) and self.__validLine(line):
                self.mainStateMachine.do(self.lineEvent(line))

        protoFile.close()

        if self.mainStateMachine.getCurrentState() == self.messageState and self.messageState.getCurrentState() == self.initState:
            self.mainStateMachine.do(self.eofEvent)

        if self.mainStateMachine.getCurrentState() != self.initState or self.messageState.getCurrentState() != self.initState:
            syntaxError = exceptions.SyntaxError()
            syntaxError.message = 'uncompleted module' + module
            raise syntaxError

    def ____topologicSortModules(self,path,modules):
        dependencyDict = {}
        for module in modules:
            dependencySet = set()
            fModule = open(os.path.join(path,module),'r')
            for line in fModule:
                line = line.strip()
                if line.startswith('include'):
                    dependency = line.replace('include','').strip()
                    dependencySet.add(dependency[1:-1])
            fModule.close()
            dependencyDict[module] = dependencySet

        from toposort  import toposort_flatten
        modules = toposort_flatten(dependencyDict)
        return modules
