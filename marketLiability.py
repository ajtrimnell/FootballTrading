import requests

class marketLiability:

    def __init__(self, matchOddsPort):
        self.response = None 
        self.matchOddsPort = matchOddsPort
            
    def request(rawRequest, port, endpoint):
        apiUrl = f"http://localhost:{port}/api/betting/v1.0/{endpoint}" 
        response = (requests.post(apiUrl, headers = {'Content-Type': 'application/json'}, data=rawRequest)).json()
        return response