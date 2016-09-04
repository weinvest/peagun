import os
import sys
import exceptions
from Common import CommonHandle
from common.ttypes import *
from get.ttypes import *

class GetHandle(CommonHandle):
    def __init__(self,m):
        super(GetHandle,self).__init__(m)

        self.handle('get:get',True,self.onRequest)

    def checkAuth(self,location,response,body):
        try:
            (userName,password,key) = self.loadAuth(location)

            if body.UserName != userName:
                response.Status = GetStatus.NoSuchUser
            elif body.Password != password:
                response.Status = GetStatus.PasswordWrong
            elif key is None or len(key) != 16:
                response.Status = GetStatus.NoData
            else:
                response.Status = GetStatus.Success
                response.Key = key
                return True

            return False
            
        except exceptions.Exception,e:
            response.Status = GetStatus.Exception
            response.Content = str(e)
            return False

    def onRequest(self,proto,spec,message,body):
        try:
            resSpec,response = self.create(message.getType(),False)
            response.Type = body.Type

            if not self.isValid(body.TradingDay):
                body.TradingDay = None

            location = self.findLocation(body.TradingDay)
            if location is None:
                response.Status = GetStatus.NoData
                return

            if self.checkAuth(location,response,body):
                if body.Type == ResType.Mapping:
                    self.getMapping(location,response,body)
                elif body.Type == ResType.Configure:
                    self.getConfigure(location,response,body)
                elif body.Type == ResType.Strategy:
                    self.getStrategy(location,response,body)
                    #debug
                    #print(self.decrypt(response.Content,response.Key))
                else:
                    response.Status = GetStatus.NotSupported

        except exceptions.Exception,e:
            response.Status = GetStatus.Exception
            response.Content = str(e)
        finally:
            self.send(proto,resSpec,response)

    def getConfigure(self,location,response,body):
        filePath = os.path.join(location,'strategy.conf') 
        if not os.path.isfile(filePath):
            response.Status = GetStatus.NoData
            return

        f = open(filePath,'r')
        response.Content = ''.join(f.readlines())

    def getStrategy(self,location,response,body):
        filePath = os.path.join(location,'strategy.bin') 
        if not os.path.isfile(filePath):
            response.Status = GetStatus.NoData
            return

        f = open(filePath,'r')
        response.Content = ''.join(f.readlines())

    def getMapping(self,location,response,body):
        filePath = os.path.join(location,'mapping.conf') 
        if not os.path.isfile(filePath):
            response.Status = GetStatus.NoData
            return

        f = open(filePath,'r')
        redirectRoot = f.readline().strip()
        if not os.path.isdir(redirectRoot):
            response.Status = GetStatus.NoData
            return

        mappings = os.listdir(redirectRoot)
        mappings.sort()
        mappings.reverse()
        for m in mappings:
            names = m.split('.')
            if 3 == len(names) and self.isValid(names[0]) and names[1] == 'mapping' and names[2] == 'csv':
                mf = open(os.path.join(redirectRoot,m))
                response.Content = ''.join(mf.readlines())
                return

