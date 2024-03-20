import requests


class Betting:

    def __init__(self, matchOddsPort, marketId, homeBetfairId, awayBetfairId, drawBetfairId):
        self.response = None 
        self.matchOddsPort = matchOddsPort
        self.marketId = marketId
        self.homeBetfairId = homeBetfairId
        self.awayBetfairId = awayBetfairId
        self.drawBetfairId = drawBetfairId
        
    def request(rawRequest, port, endpoint):
        apiUrl = f"http://localhost:{port}/api/betting/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=rawRequest)).json()
        return response


class PlaceBet(Betting):

    def __init__(self):
        super().__init__()
          
    def placeBet(self, marketId, selectionId, betType, price, stake):
        self.rawRequest = f'{"marketId":"{marketId}","globalSettings":{"action":"NONE"},"async":false,"betsToPlace":[{"selectionId":"{selectionId}" \
                                ,"type":"{betType}","bspBetType":"NOT_BSP","price":{price},"stake":{stake}}]}'
        return (requests.post(self.rawRequest, self.matchOddsPort, 'PlaceBets'))
    

class MarketLiability(Betting):
    
    def __init__(self, betId):
        super().__init__()
        self.betId = betId
    
    def betStatus(self, marketId, betId):
        self.rawRequest = f'{"marketId":"{marketId}","pendingResultId":"{betId}"}'
        return (requests.post(self.rawRequest, self.matchOddsPort, 'getPendingResultId'))
    
    
    