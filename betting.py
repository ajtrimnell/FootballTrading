import requests


class Betting:

    def __init__(self, marketId, eventId, **kwargs):

        self.marketId = marketId
        self.eventId = eventId
        
        self.betsStatus = kwargs.get('betStatus') 
        self.selectionId = kwargs.get('selectionId')
        self.homeBetfairId = kwargs.get('homeBetfairId')
        self.awayBetfairId = kwargs.get('awayBetfairId')
        self.drawBetfairId = kwargs.get('drawBetfairId') 
        
        self.currentGreeningProfitOrLoss = 0
        self.currentMarketLiability = 0
        self.totalMarketBackBets = 0
        self.totalMarketLayBets = 0
        
        self.currentNetPosition = 0
    
    
    def request(rawRequest, url1, endpoint):
        apiUrl = f"http://localhost:9000/api/{url1}/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=rawRequest)).json() 
        return response
    
    # If this returns two empty lists; there have been no bets placed on this market that have been matched
    def getMarketBets(self):
        rawRequest = f'{{"marketId":"{self.marketId}","filter":{{"option":"{self.betsStatus}"}}}}'
        return Betting.request(rawRequest, 'markets', 'getMarketBets')
    
    # From Bet Angel stored values          
    def marketStoredValues(self):
        rawRequest = f'{{"marketsFilter":{{"filter":"SPECIFIED_IDS","ids":["{self.marketId}"]}},"selectionsFilter":{{"filter":"ALL"}},"storedValueFilterMarketLevel":\
                    {{"storedValueFilter":"ALL","excludeSharedValues":true}},"storedValueFilterSelectionLevel":{{"storedValueFilter":"ALL","excludeSharedValues":true}}}}'
        storedValues = Betting.request(rawRequest, 'automation', 'getStoredValues')['result']['markets'][0]['instances'][0]['values']
        
        # Bet Angel stored values are returned in alphabetical order
        self.currentGreeningProfitOrLoss = storedValues[0].get('v')
        self.currentMarketLiability = storedValues[1].get('v')
        self.totalMarketBackBets = storedValues[2].get('v')
        self.totalMarketLayBets = storedValues[3].get('v')
        
        return 
    
    
    def placeBet(self, betType, price, stake):
        rawRequest = f'{{"marketId":"{self.marketId}","globalSettings":{{"action":"NONE"}},"async":true,"betsToPlace":[{{"selectionId":"{self.selectionId}"\
                        ,"type":"{betType}","bspBetType":"NOT_BSP","price":{price},"stake":{stake}}}]}}'                       
        return Betting.request(rawRequest, 'betting', 'placeBets')


    def getPendingPlaceBetsResult(self, betId):
        rawRequest = f'{"marketId":"{self.marketId}","pendingResultId":"{betId}"}'
        return Betting.request(rawRequest, 'betting', 'getPendingPlaceBetsResult')


    def marketNetPosition(self):
        self.currentNetPosition = self.currentGreeningProfitOrLoss - self.currentMarketLiability
        return 

    

    # def placeBets(self):
        
        
        
# x = Betting('1.225968849').getMarketBets()


# from pprint import pprint
# pprint(x)

   





    