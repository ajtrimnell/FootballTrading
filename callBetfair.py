import requests

class CallBetfair:

    def __init__(self, matchOddsPort, matchOddsPlusOnePort, correctScorePort, goalMarketsPort):
        self.response = None 
        self.matchOddsPort = matchOddsPort
        self.matchOddsPlusOnePort = matchOddsPlusOnePort
        self.correctScorePort = correctScorePort
        self.goalMarketsPort = goalMarketsPort
        
    def request(endpoint, dataRequired, port, path):
        apiUrl = f"http://localhost:{port}/api/{path}/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=dataRequired)).json()
        return response

    def markets(self):  
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","NAME","MARKET_START_TIME","MARKET_INPLAY_STATUS","EVENT_ID","EVENT_TYPE_ID","MARKET_TYPE","SELECTION_IDS","SELECTION_NAMES"]}' 
        return (CallBetfair.request(endpoint, dataRequired, self.matchOddsPort, 'markets')).get('result',{}).get('markets')
    
    # Market prices are returned from the stored values in Bet Angel
    def marketPrices(self):
        endpoint = "getStoredValues"
        dataRequired = '{"marketsFilter":{"filter":"ALL"},"selectionsFilter":{"filter":"ALL"},"storedValueFilterBetAngelLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterEventLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterMarketLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterSelectionLevel":{"storedValueFilter":"ALL","excludeSharedValues":true}}'
        return CallBetfair.request(endpoint, dataRequired, self.matchOddsPort, 'automation')
    
    # Return all stored values except for the market prices. Stored values being returned are marked as 'shared' in Bet Angel
    def storedValues(self, marketId):
        endpoint = "getStoredValues"
        dataRequired = f'{{"marketsFilter":{{"filter":"SPECIFIED_IDS","ids":["{marketId}"]}},"selectionsFilter":{{"filter":"ALL"}},"storedValueFilterMarketLevel":{{"storedValueFilter":"ALL","excludeInstanceValues":true}},"storedValueFilterSelectionLevel":{{"storedValueFilter":"ALL","excludeInstanceValues":true}}}}'
        return CallBetfair.request(endpoint, dataRequired, self.matchOddsPort, 'automation')
    
    def plusOneMarkets(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","NAME","MARKET_START_TIME","MARKET_INPLAY_STATUS","EVENT_ID","EVENT_TYPE_ID","MARKET_TYPE","SELECTION_IDS","SELECTION_NAMES"]}' 
        return (CallBetfair.request(endpoint, dataRequired, self.matchOddsPlusOnePort, 'markets')).get('result',{}).get('markets')
    
    def plusOneMarketPrices(self):
        endpoint = "getStoredValues"
        dataRequired = '{"marketsFilter":{"filter":"ALL"},"selectionsFilter":{"filter":"ALL"},"storedValueFilterBetAngelLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterEventLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterMarketLevel":{"storedValueFilter":"ALL","excludeSharedValues":true},"storedValueFilterSelectionLevel":{"storedValueFilter":"ALL","excludeSharedValues":true}}'
        return CallBetfair.request(endpoint, dataRequired, self.matchOddsPlusOnePort, 'automation').get('result',{}).get('markets')
    
    def goalMarkets(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","MARKET_INPLAY_STATUS","EVENT_ID","MARKET_TYPE"]}' 
        return CallBetfair.request(endpoint, dataRequired, self.goalMarketsPort, 'markets').get('result',{}).get('markets')
    
    def correctScore(self):
        endpoint = "getMarkets"      
        dataRequired = '{"dataRequired":["ID","MARKET_INPLAY_STATUS","EVENT_ID","MARKET_TYPE"]}' 
        return CallBetfair.request(endpoint, dataRequired, self.correctScorePort, 'markets').get('result',{}).get('markets')
    
    def __repr__(self):
        return self.markets