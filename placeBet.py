import requests

class PlaceBet:
    
    def __init__(self, matchOddsPort):
        self.response = None 
        self.matchOddsPort = matchOddsPort
        
    def request(dataRequired, port, path):
        apiUrl = f"http://localhost:{port}/api/{path}/v1.0/placeBets" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=dataRequired)).json()
        return response
          
    def placeBet(self, marketId, selectionId, betType, price, stake):
        
        self.dataRequired = f'{"marketId":"{marketId}","globalSettings":{"action":"NONE"},"async":true,"betsToPlace":[{"selectionId":"{selectionId}" \
                                ,"type":"{betType}","bspBetType":"NOT_BSP","price":{price},"stake":{stake}}]}'
        
        return
    
    