import requests


class Betting:

    def __init__(self, marketId):
        # , homeBetfairId, awayBetfairId, drawBetfairId):
        # self.response = None 
        # self.matchOddsPort = matchOddsPort
        self.marketId = marketId
        
        # self.homeBetfairId = homeBetfairId
        # self.awayBetfairId = awayBetfairId
        # self.drawBetfairId = drawBetfairId
    
    # def __init__(self, matchOddsPort, marketId, **kwargs):
    
    def request(rawRequest, url1, endpoint):
        apiUrl = f"http://localhost:9000/api/{url1}/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=rawRequest)).json() 
        return response


# class PlaceBet(Betting):

#     def __init__(self):
#         super().__init__()
          
#     def placeBet(self, marketId, selectionId, betType, price, stake):
        
#         # request1 = f'{{"marketId":"{marketId}"'
        
#         self.rawRequest = f'{{"marketId":"{marketId}","globalSettings":{"action":"NONE"},"async":false,"betsToPlace":[{"selectionId":"{selectionId}" \
#                                 ,"type":"{betType}","bspBetType":"NOT_BSP","price":{price},"stake":{stake}}]}}'
                                
#         print(self.rawRequest)
        
#         return (requests.post(self.rawRequest, self.matchOddsPort, 'PlaceBets'))
    

class CheckMarketBets(Betting):

    def __init__(self, marketId, betsStatus):
        super().__init__(marketId)
        self.betsStatus = betsStatus
        
    def getBets(self):
        self.rawRequest = f'{{"marketId":"{self.marketId}","filter":{{"option":"{self.betsStatus}"}}}}'
        return Betting.request(self.rawRequest, 'markets', 'getMarketBets')
     


class MarketLiability(Betting):
    
    def __init__(self, betId):
        super().__init__()
        self.betId = betId
    
    def betStatus(self, marketId, betId):
        self.rawRequest = f'{"marketId":"{marketId}","pendingResultId":"{betId}"}'
        return (requests.post(self.rawRequest, self.matchOddsPort, 'getPendingResultId'))
    
    
    