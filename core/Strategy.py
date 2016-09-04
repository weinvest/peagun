from pyquant.network import WProto
from pyquant.proto.strategy.ttypes import *
from pyquant.proto.strategy.constants import *
from pyquant.network.WSignal import WSignal
from pyquant.core.ParamsChecker import ParamChecker

class StrategyClient(WProto):
    onAddStrategy = WSignal()
    onGetStrategy = WSignal()
    onUpdateStrategy = WSignal()
    onListStrategy = WSignal()
    onSubscribeTrading = WSignal()
    onUnsubscribeTrading = WSignal()
    onTradingNotify = WSignal()
    onDeployBackTest = WSignal()
    
    onDeploySimulation = WSignal()
    onDisableSimulation = WSignal()
    onEnableSimulation = WSignal()
    
    onDeployLive = WSignal()
    onDisableLive = WSignal()
    onEnableLive = WSignal()
    
    def __init__(self):
        WProto.__init__(self)
        
        self.dispatchDict = {
        WMESSAGE_STRATEGY_ADD_STRATEGY:DispatchItem(AddStrategyResponse, self.onAddStrategy), 
        WMESSAGE_STRATEGY_GET_STRATEGY:DispatchItem(GetStrategyResponse, self.onGetStrategy), 
        WMESSAGE_STRATEGY_UPDATE_STRATEGY:DispatchItem(UpdateStrategyResponse, self.onUpdateStrategy), 
        WMESSAGE_STRATEGY_LIST_STRATEGIES:DispatchItem(ListStratgyResponse, self.onListStrategy), 
        WMESSAGE_STRATEGY_SUBSCRIBE_TRADING:DispatchItem(SubscribeTradingResponse, self.onSubscribeTrading) , 
        WMESSAGE_STRATEGY_UNSUBSCRIBE_TRADING: DispatchItem(UnSubscribeTradingResponse, self.onUnsubscribeTrading), 
        WMESSAGE_STRATEGY_TRADING_NOTIFY: DispatchItem(TradingNotify, self.onTradingNotify), 
        WMESSAGE_STRATEGY_DEPLOY_BACKTEST:DispatchItem(DeployBackTestResponse, self.onDeployBackTest), 
        WMESSAGE_STRATEGY_DEPLOY_STRATEGY:DispatchItem(DeploySimulationResponse, self._onDeployStrategy), 
        WMESSAGE_STRATEGY_DISABLE_STRATEGY: DispatchItem(DisableStrategyResponse, self._onDisableStrategy), 
        WMESSAGE_STRATEGY_ENABLE_STRATEGY:DispatchItem(EnableStrategyResponse, self._onDisableStrategy)
        }
    def addStrategy(self, sessionId, strategyName, content, key):
        ParamChecker.checkNotNull(strategyname = strategyName, strategyContent = content , key = key)
        addStrategyRequest = AddStrategyRequest()
        addStrategyRequest.StrategyName = strategyName
        addStrategyRequest.StrategyContent = content
        addStrategyRequest.Key = key
        
        self.send(sessionId, WMESSAGE_STRATEGY_ADD_STRATEGY, addStrategyRequest)
        
    def getStrategy(self, sessionId, strategyId):
        getStrategyRequest = GetStrategyRequest()
        getStrategyRequest.StrategyId = strategyId
        
        self.send(sessionId,WMESSAGE_STRATEGY_GET_STRATEGY, getStrategyRequest)
        
    def updateStrategy(self, sessionId, strategyId, strategyName, content):
        updateStrategyRequest = UpdateStrategyRequest()
        updateStrategyRequest.StrategyId = strategyId
        updateStrategyRequest.StrategyName = strategyName
        updateStrategyRequest.StrategyContent = content
        
        self.send(sessionId, WMESSAGE_STRATEGY_UPDATE_STRATEGY, updateStrategyRequest)
        
    def listStrategy(self, sessionId):
        self.send(sessionId,WMESSAGE_STRATEGY_LIST_STRATEGIES)
        
    def subscribeTrading(self, sessionId, strategyId):
        subscribeRequest = SubscribeTradingRequest()
        subscribeRequest.StrategyId = strategyId
        
        self.send(sessionId, WMESSAGE_STRATEGY_SUBSCRIBE_TRADING, subscribeRequest)
        
    def unsubscribeTrading(self, sessionId, strategyId):
        unsubscribeRequest = UnSubscribeTradingRequest()
        unsubscribeRequest.StrategyId = strategyId
        
        self.send(sessionId, WMESSAGE_STRATEGY_UNSUBSCRIBE_TRADING, unsubscribeRequest)
    def deployBackTest(self, sessionId, strategyId, begTime, endTime, interval = 500):
        deployBackTest = DeployBackTestRequest()
        deployBackTest.StrategyId = strategyId
        deployBackTest.BeginTime = begTime
        deployBackTest.EndTime = endTime
        deployBackTest.Interval = interval
        
        self.send(sessionId,WMESSAGE_STRATEGY_DEPLOY_BACKTEST, deployBackTest)
    
    def __deployStrategy(self, sessionId, strategyId, deployType):
        deployRequest = DeployStrategyRequest()
        deployRequest.StrategyId = strategyId
        deployRequest.DeployType = deployType
        
        self.send(sessionId, WMESSAGE_STRATEGY_DEPLOY_STRATEGY, deployStrategy)

    def __disableStrategy(self, sessionId, strategyId, deployType):
        disableRequest = DisableStrategyRequest()
        disableRequest.StrategyId = strategyId
        disableRequest.DeployType = deployType
        
        self.send(sessionId, WMESSAGE_STRATEGY_DISABLE_STRATEGY, disableRequest)
    
    def __enableStrategy(self, sessionId, StrategyId, deployType):
        enableRequest = EnableStrategyRequest()
        enableRequest.StrategyId = StrategyId
        enableRequest.DeployType = deployType
        
        self.send(sessionId, WMESSAGE_STRATEGY_ENABLE_STRATEGY, enableRequest)
        
    def deploySimulation(self, sessionId, strategyId):
        self.__deployStrategy(sessionId, strategyId, EDeployType.Simulation)
          
    def disableSimulation(self, sessionId, strategyId):
        self.__disableStrategy(sessionId, strategyId, EDeployType.Simulation)
        
    def enableSimulation(self, sessionId, strategyId):
        self.__enableStrategy(sessionId, strategyId, EDeployType.Simulation)
        
    def deployLive(self, sessionId, strategyId):
        self.__deployStrategy(sessionId, strategyId, EDeployType.Live)
        
    def disableLive(self, sessionId, strategyId):
        self.__disableStrategy(sessionId, strategyId, EDeployType.Live)
        
    def enableLive(self, sessionId, strategyId):
        self.__enableStrategy(sessionId, strategyId, EDeployType.Live)

    def _onDeployStrategy(self, sessionId, message):
        if  message.DeployType == EDeployType.Simulation:
            self.onDeploySimulation(sessionId, message)
        else:
            self.onDeployLive(sessionId, message)
    
        
    def _onDisableStrategy(self, sessionId, message):
        if  message.DeployType == EDeployType.Simulation:
            self.onDisableSimulation(sessionId, message)
        else:
            self.onDisableLive(sessionId, message)
        
    def _onEnableStrategy(self, sessionId, message):
        if  message.DeployType == EDeployType.Simulation:
            self.onEnableSimulation(sessionId, message)
        else:
            self.onEnableLive(sessionId, message)
