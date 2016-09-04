import os
import exceptions
from  datetime  import  *
from Common import CommonHandle
from put.ttypes import *
from common.ttypes import *

class PutHandle(CommonHandle):
    def __init__(self,m):
        super(PutHandle,self).__init__(m)

        self.handle('put:put',True,self.onPut)
        self.handle('auth:put',True,self.onAuth)
        self.handle('update:put',True,self.onUpdate)
    def randString(self,length):
        from random import sample
        chars = sample(list('AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789!@#$%^&*)'),length)
        return ''.join(chars)


    def onPut(self,proto,spec,message,body):
        try:
            responseSpec,response = self.create(message.getType(),False)
            response.Type = body.Type

            if not self.isValid(body.TradingDay):
                body.TradingDay = date.today().strftime('%Y%m%d')

            location = os.path.join(self.dbRoot,body.TradingDay)
            if not os.path.exists(location):
                os.mkdir(location)
                fAuth = open(os.path.join(location,'.auth'),'w')
                userName = self.randString(8)
                passWord = self.randString(12)
                key = self.randString(16)
                jsonObj = {'UserName':userName,'Password':passWord,'Key':key}

                import json
                json.dump(jsonObj,fAuth)
                fAuth.close()

            fileName = {ResType.Mapping:self.mappingFileName
                        ,ResType.Configure:self.strategyConfFileName
                        ,ResType.Strategy:self.strategyBinFileName}[body.Type]
            writePath = os.path.join(location,fileName)
            if os.path.exists(writePath):
                response.Status = PutStatus.Exists
                return

            (userName,passWord,key) = self.loadAuth(location)

            self.writeBody(body,writePath,key)

            response.Status = PutStatus.Success
            response.UserName = userName
            response.Password = passWord
        except exceptions.Exception,e:
            response.Status = PutStatus.Exception
            response.UserName = str(e)
        finally:
            self.send(proto,responseSpec,response)


    def writeBody(self,body,writePath,key):
        if body.Type == ResType.Strategy:
            import bz2
            compressedFile = bz2.BZ2File(writePath,'w')
            compressedFile.write(self.encrypt(body.Content,key))
            compressedFile.close()
        else:
            fwrite = open(writePath,'w')
            if body.Type == ResType.Mapping:
                fwrite.write(body.Content)
            else:
                encryptedBody = self.encrypt(body.Content,key)
                fwrite.write(encryptedBody)
            fwrite.close()

    def onAuth(self,proto,spec,message,body):
        try:
            authSpec,authResponse = self.create(message.getType(),False)
            location = self.findLocation(body.TradingDay)
            if not os.path.isfile(os.path.join(location,self.authFileName)):
                authResponse.Status = AuthStatus.NotExists
                return

            (authResponse.UserName,authResponse.Password,key) = self.loadAuth(location)
            authResponse.Status = AuthStatus.Success

        except exceptions.Exception,e:
            authResponse.Status = AuthStatus.Exception
            authResponse.UserName = str(e)
        finally:
            self.send(proto,authSpec,authResponse)

    def onUpdate(self,proto,spec,message,body):
        try:
            responseSpec,response = self.create(message.getType(),False)
            response.Type = body.Type

            location = self.findLocation(body.TradingDay)

            fileName = {ResType.Mapping:self.mappingFileName
                        ,ResType.Configure:self.strategyConfFileName
                        ,ResType.Strategy:self.strategyBinFileName}[body.Type]
            writePath = os.path.join(location,fileName)
            if not os.path.exists(writePath):
                response.Status = UpdateStatus.NotExists
                return

            (userName,passWord,key) = self.loadAuth(location)
            if None in (userName,passWord,key):
                response.Status = UpdateStatus.NotExists
                return

            self.writeBody(body,writePath,key)

            response.Status = UpdateStatus.Success
        except exceptions.Exception,e:
            response.Status = UpdateStatus.Exception
        finally:
            self.send(proto,responseSpec,response)
