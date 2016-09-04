from pyquant.network import WProto
from pyquant.proto.login.ttypes import *
from pyquant.proto.login.constants import *
from pyquant.network.WSignal import WSignal
from pyquant.core.ParamsChecker import ParamChecker
class LoginClient(WProto):
    onRegiste = WSignal() // onRegiste(RegisteResponse)
    onLogin = WSignal()  // onLogin()
    onLogout = WSignal()
    onChangeKey = WSignal()
    onChangePassword = WSignal()
    onLoginAtOtherAddress = WSignal()
    onOtherLogout = WSignal()
    
    def __init__(self):
        WProto.__init__(self)
        
        self.dispatchDict = {
        WMESSAGE_LOGIN_REGISTE: DispatchItem(RegisteResponse, self.onRegiste), 
        WMESSAGE_LOGIN_LOGIN: DispatchItem(LoginResponse, self.onLogin), 
        WMESSAGE_LOGIN_LOGOUT:DispatchItem(LogoutResponse, self.onLogout), 
        WMESSAGE_LOGIN_CHANGE_KEY: DispatchItem(ChangeKeyResponse, self.onChangeKey), 
        WMESSAGE_LOGIN_CHANGE_PASSWORD:DispatchItem(ChangePassword, self.onChangePassword), 
        WMESSAGE_LOGIN_LOGIN_NOTIFY:DispatchItem(LoginNotify, self.onLoginAtOtherAddress), 
        WMESSAGE_LOGIN_LOGOUT_NOTIFY:DispatchItem(LogoutNotify, self.onOtherLogout)
        }
    
    def registe(self,reqestId,  userName, password, email, securityCode, publicKey = None, privateKey = None,mobile = None):
        ParamChecker.checkNotNull(username = userName, password=password, email=email, securitycode=securityCode)
        
        registeRequest = RegisteRequest()
        registeRequest.UserName = userName 
        registeRequest.Password = password
        registeRequest.Email = email
        registeRequest.SecurityCode = securityCode
        registeRequest.PublicKey = publicKey
        registeRequest.PrivateKey = privateKey
        registeRequest.Mobile = mobile
        
        self.send(reqestId, WMESSAGE_LOGIN_REGISTE, registeRequest)
    
    def login(self, requestId, userName, password, securityCode = None):
        ParamChecker.checkNotNull(username = userName, password = password)
        
        loginRequest = LoginRequest()
        loginRequest.UserName = userName
        loginRequest.Password = password
        loginRequest.SecurityCode = securityCode
        
        self.send(reqestId, WMESSAGE_LOGIN_LOGIN, loginRequest)
    
    def loginout(self, sessionId):    
        self.send(sessionId, WMESSAGE_LOGIN_LOGOUT)
    
    def changeKey(self, sessionId, publicKey, privateKey):
        ParamChecker.checkNotNull(publickey=publicKey, privatekey=privateKey)
        
        changeKeyRequest = ChangeKeyRequest()
        changeKeyRequest.PublicKey = publicKey
        changeKeyRequest.PrivateKey = privateKey
        
        self.send(sessionId, WMESSAGE_LOGIN_CHANGE_KEY, changeKeyRequest)
        
    def changePassword(self, sessionId, oldPassword, newPassword):
        ParamChecker.checkNotNull(oldpassword = oldPassword, newpassword = newPassword)
        
        changePasswordRequest = ChangePasswordRequest()
        changePasswordRequest.OldPassword = oldPassword
        changePasswordRequest.NewPassword = newPassword
        
        self.send(sessionId, WMESSAGE_LOGIN_CHANGE_PASSWORD, changePasswordRequest)
        
