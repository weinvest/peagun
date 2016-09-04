from pyquant.network import WProto
from pyquant.proto.plugin.ttypes import *
from pyquant.proto.plugin.constants import *
from pyquant.network.WSignal import WSignal
from pyquant.core.ParamsChecker import ParamChecker

class PluginClient(WProto):
    onListPlugin = WSignal()
    onPutPlugin = WSignal()
    onGetPluginParams = WSignal()
    onDeletePlugin = WSignal()
    onGetHotPlugins = WSignal()
    onBuyPlugin = WSignal()
    
    def __init__(self):
        WProto.__init__(self)
        self.dispatchDict = {
        WMESSAGE_PLUGIN_LIST_PLUGIN: DispatchItem(ListPluginResponse, self.onListPlugin), 
        WMESSAGE_PLUGIN_PUT_PLUGIN:DispatchItem(PutPluginResponse, self.onPutPlugin), 
        WMESSAGE_PLUGIN_DELETE_PLUGIN:DispatchItem(DeletePluginResponse, self.onDeletePlugin), 
        WMESSAGE_PLUGIN_GET_PLUGIN_PARAMS:DispatchItem(GetPluginParamsResponse, self.onGetPluginParams), 
        WMESSAGE_PLUGIN_GET_HOT_PLUGINS:DispatchItem(GetHotPluginResponse, self.onGetHotPlugins), 
        WMESSAGE_PLUGIN_BUY_PLUGIN:DispatchItem(BuyPluginResponse, self.onBuyPlugin)
        }
    
    def listPlugin(self, sessionId, pluginType):
        
        listPluginRequest = ListPluginRequest()
        listPluginRequest.Type = pluginType
        
        self.send(sessionId, WMESSAGE_PLUGIN_LIST_PLUGIN, listPluginRequest)
    
    def putPlugin(self, sessionId,pluginType, pluginName, securityText, key, isDebug = false):
        putPluginRequest = PutPluginRequest()
        putPluginRequest.Type = pluginType
        putPluginRequest.PluginName = pluginName;
        putPluginRequest.SecurityText = securityText
        putPluginRequest.Key = key
        putPluginRequest.IsDebug = isDebug
        
        self.send(sessionId, WMESSAGE_PLUGIN_PUT_PLUGIN, putPluginRequest)
        
    def deletePlugin(self, sessionId, pluginId):
        deletePluginRequest = DeletePluginRequest()
        deletePluginRequest.PluginId = pluginId
        
        self.send(sessionId, WMESSAGE_PLUGIN_DELETE_PLUGIN, deletePluginRequest)
    
    def getPluginParams(self, session, pluginId):
        getPluginParamsRequest = GetPluginParamsRequest()
        getPluginParamsRequest.PluginId = pluginId
        
        self.send(sessionId, WMESSAGE_PLUGIN_GET_PLUGIN_PARAMS, getPluginParamsRequest)
        
    def getHotPlugins(self, requestId, sortField, offset, maxCount):
        ParamChecker.checkIsIn(["UsedCount", "AveragePNL"], sortfield = sortField)
        
        getHotPluginRequest = GetHotPluginsRequest()
        getHotPluginRequest.SortField = sortField
        getHotPluginRequest.Offset = offset
        getHotPluginRequest.MaxCount = maxCount
        
        self.send(requestId, WMESSAGE_PLUGIN_GET_HOT_PLUGINS, getHotPluginRequest)
        
    def buyPlugin(self, sessionId, pluginId, payId):
        buyPluginRequest = BuyPluginRequest()
        buyPluginRequest.PluginId = pluginId
        buyPluginRequest.PayId = payId
        
        self.send(sessionId, WMESSAGE_PLUGIN_BUY_PLUGIN, buyPluginRequest)
        
