import os
import sys
import re
import exceptions


class MessagePlugin(object):
    def __init__(self, mesgHandle):
        self.mesgHandle = mesgHandle
        self.info = mesgHandle.info
        self.error = mesgHandle.error
        self.warn = mesgHandle.warn
        self.show = mesgHandle.show
        self.user = mesgHandle.user
        self.ignore = mesgHandle.ignore
        self.handle = mesgHandle.handle
        self.send = mesgHandle.send

        self.create = mesgHandle.create
        mesgHandle.addPlugin(self)

    def onConnectionOpened(self, proto):
        pass

    def onConnectionClosed(self, proto, reason):
        pass


class MessageHandler(object):
    def __init__(self):
        self.dispatchDict = {}
        self.plugins = []
        self.default = self.user

    def setView(self, view):
        self.view = view

    def addPlugin(self, plugin):
        self.plugins.append(plugin)

    def onConnectionOpened(self, proto):
        for plugin in self.plugins:
            plugin.onConnectionOpened(proto)

    def onConnectionClosed(self, proto, reason):
        for plugin in self.plugins:
            plugin.onConnectionClosed(proto,reason)

    def onMessage(self, proto, message):
        (spec, body) = self.view.deserialize(message)
        handles = self.dispatchDict.get((spec.getMessageName(), message.isInitiator()))
        if handles is None:
            self.default(proto, spec, message, body)
        else:
            for mesgHandle in handles:
                mesgHandle(proto, spec, message, body)

        return (spec, body)

    def handle(self, mesgType, isInitiator, handler):
        if not self.dispatchDict.has_key((mesgType, isInitiator)):
            self.dispatchDict[(mesgType, isInitiator)] = [handler]
        else:
            self.dispatchDict[(mesgType, isInitiator)].append(handler)

    def info(self, mesg):
        self.view.info(mesg)

    def error(self, mesg):
        self.view.error(mesg)

    def warn(self, mesg):
        self.view.warn(mesg)

    def ignore(self, proto, spec, message, body):
        pass

    def user(self, proto, spec, message, body):
        self.view.user(proto, spec, message, body)

    def show(self, proto, spec, message, body):
        self.view.show(proto, spec, message, body)

    def create(self, nameOrCode, isInitiator):
        return self.view.create(nameOrCode, isInitiator)

    def send(self,proto,spec,body):
        return self.view.send(proto,spec,body)


class Factory(object):
    @staticmethod
    def createPlugin(root, pluginName, mesgHandle):
        try:
            module = __import__(pluginName)
            constructor = getattr(module, pluginName)
            if constructor is not None:
                return constructor(mesgHandle)
        except exceptions.Exception, e:
            print('create plugin exception:' + str(e))
            return None

    @staticmethod
    def findPlugins(pattern):
        if pattern is None:
            return (None,{})

        [root, fileNames] = os.path.split(pattern)
        if not os.path.exists(root):
            print(pattern + ' is not a valid path')
            return (root,[])

        rePattern = re.compile(fileNames)
        allFiles = os.listdir(root)

        files = []
        for f in allFiles:
            fileName, ext = os.path.splitext(f)
            if ext == '.py' and rePattern.match(fileName):
                files.append(fileName)
        return (root,files)

    @staticmethod
    def createMessageHandle(pattern):
        mesgHandle = MessageHandler()
        root,plugins = Factory.findPlugins(pattern)
        if 0 != len(plugins):
            sys.path.append(root)
            for plugin in plugins:
                Factory.createPlugin(root, plugin, mesgHandle)

        return mesgHandle
