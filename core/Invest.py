from pyquant.network import WProto
from pyquant.proto.invest.ttypes import *
from pyquant.proto.invest.constants import *
from pyquant.network.WSignal import WSignal
from pyquant.core.ParamsChecker import ParamChecker

class InvestClient(WProto):
    onListInvest = WSignal()
    onGetInvestPerformance = WSignal()
    onInvest  = WSignal()
    onDisinvest = WSignal()
    
    def __init__(self):
        WProto.__init__(self)
        
        self.dispatchDict = {
        WMESSAGE_INVEST_LIST_INVESTS:DispatchItem(ListInvestsResponse, self.onListInvest), 
        WMESSAGE_INVEST_GET_PERFORMANCE:DispatchItem(GetInvestPerformanceResponse, self.onGetInvestPerformance), 
        WMESSAGE_INVEST_INVEST:DispatchItem(InvestResponse, self.onInvest), 
        WMESSAGE_INVEST_DISINVEST:DispatchItem(DisInvestResponse, self.onDisinvest)
        }
    
    def listInvest(self, sessionId):
        self.send(sessionId, WMESSAGE_INVEST_LIST_INVESTS)
        
    def getInvestPerformance(self, sessionId, investId, begTime, interval, maxCount):
        getPerformanceRequest = GetInvestPerformanceRequest()
        getPerformanceRequest.InvestId = investId
        getPerformanceRequest.FromTime = begTime
        getPerformanceRequest.IntervalDay = interval
        getPerformanceRequest.MaxCount = maxCount
        
        self.send(sessionId,WMESSAGE_INVEST_GET_PERFORMANCE, getPerformanceRequest)
        
    def invest(self, sessionId, strategyId, delayPayId, investment):
        investRequest = InvestRequest()
        investRequest.StrategyId = strategyId
        investRequest.DelayPayId = delayPayId
        investRequest.Investment = investment
        
        self.send(sessionId,WMESSAGE_INVEST_INVEST, investRequest)
        
    def disinvest(self, sessionId,investId, investment):
        disinvestRequest = DisInvestRequest()
        disinvestRequest.InvestId = investId
        disinvestRequest.Investment = investment
        
        self.send(sessionId,WMESSAGE_INVEST_DISINVEST,disinvestRequest)
        
