from pyquant.network import WProto
from pyquant.proto.rank.ttypes import *
from pyquant.proto.rank.constants import *
from pyquant.network.WSignal import WSignal
from pyquant.core.ParamsChecker import ParamChecker

class RankClient(WProto):
    onGetRank = WSignal()
    onGetPerformance = WSignal()
    
    def __init__(self):
        WProto.__init__(self)
        
        self.dispatchDict = {
            WMESSAGE_RANK_GET_RANKS, DispatchItem(GetRankResponse, self.onGetRank), 
            WMESSAGE_RANK_GET_PERFORMANCE, DispatchItem(GetPerformanceResponse, self.onGetPerformance)
        }
        
    def getRank(self, requestId, runMode, sortField, offset, maxCount=20):
        ParamChecker.checkIsIn(['PNL7', 'PNL30', "PNL180", 'TotalInvestment', 'TotalPNL', 'Sharp'], sortfield = sortField )
        ParamChecker.checkIsInstance(StrategyRunMode, runmode = runMode)
        
        getRankRequest = GetRankRequest()
        getRankRequest.StrategyRunMode = runMode
        getRankRequest.SortField = sortField
        getRankRequest.Offset = offset;
        getRankRequest.MaxCount = maxCount
        
        self.send(WMESSAGE_RANK_GET_RANKS, requestId, getRankRequest)
    
    def getPerformance(self, requestId, strategyId, runMode, interval = 1):
        ParamChecker.checkIsInstance(StrategyRunMode, runmode = runMode)
        
        getPerformanceRequest.StrategyId = strategyId;
        getPerformanceRequest.RunMode = runMode
        getPerformanceRequest.IntervalDay = interval
        
        self.send(WMESSAGE_RANK_GET_PERFORMANCE, requestId, getPerformanceRequest)
