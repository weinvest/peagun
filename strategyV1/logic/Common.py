import os
import exceptions
from MessageHandler import MessagePlugin

class CommonHandle(MessagePlugin):
    authFileName = '.auth'
    strategyConfFileName = 'strategy.conf'
    strategyBinFileName = 'strategy.bin'
    mappingFileName = 'mapping.conf'
    dbRoot = '.v1db'

    def __init__(self,m):
        super(CommonHandle,self).__init__(m)

    def onConnectionOpened(self,proto):
        pass


    def encrypt(self,content,key):
        diredLen = len(content)
        restLen = diredLen % 16
        if 0 != restLen:
            appLen = 16 - restLen
            content += ' ' * appLen

        from Crypto.Cipher import AES
        encryptor = AES.new(key,AES.MODE_CBC,'\0'*16)
        content = encryptor.encrypt(content)
        return content

    def decrypt(self,content,key):
        from Crypto.Cipher import AES
        decryptor = AES.new(key,AES.MODE_CBC,'\0'*16)
        content = decryptor.decrypt(content)
        return content

    def onConnectionClosed(self,proto,reason):
        pass

    def isValid(self,d):
        try:
            if d is None:
                return False

            if len(d) == 8:
                year = int(d[:4])
                month = int(d[4:6])
                day = int(d[6:8])
                return month >= 1 and month <= 12 and day >= 1 and day <= 31
            else:
                return False
        except exceptions.Exception:
            return False

    def findLocation(self,tradingDay):
        if not self.isValid(tradingDay):
            tradingDay = None

        root = self.dbRoot
        if not os.path.exists(root):
            return None
        elif tradingDay is not None and os.path.isdir(os.path.join(root,tradingDay)):
            return os.path.join(root,tradingDay)

        dirs = os.listdir(root)
        dirs.sort()
        dirs.reverse()
        for d in dirs:
            location = os.path.join(root,d)
            if os.path.isdir(location):
                if self.isValid(d):
                    return location
        return None

    def loadAuth(self,location):
        authFilePath = os.path.join(location,self.authFileName)
        if not os.path.isfile(authFilePath):
            return (None,None,None)

        import json
        try:
            fAuth = open(authFilePath,'r')
            authObj = json.load(fAuth)
            return (authObj.get('UserName'),authObj.get('Password'),authObj.get('Key'))
        except exceptions.Exception,e:
            return (None,None,None)