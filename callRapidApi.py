import requests
from pprint import pprint
import json

from teamsDictionary import teamsDictionary

class RapidApi:
    
    def __init__(self, date, league, season):   
        self.date = date
        self.league = league
        self.season = season
		 
   
    def todaysFixtures(self):     
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        headers = {"X-RapidAPI-Key": "fc14be64fbmshba994557bc79feep15806fjsn401a0940a28f",
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}

        self.querystring = {'date': self.date, 'league': self.league,'season': self.season}
        self.response = requests.get(url, headers=headers, params=self.querystring).json()
        return self.response
   
   
    def inplayMatches(self):
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        headers = {"X-RapidAPI-Key": "fc14be64fbmshba994557bc79feep15806fjsn401a0940a28f",
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}

        self.querystring = {'live':'all', 'league': self.league,'season': self.season}
        self.response = requests.get(url, headers=headers, params=self.querystring).json()
        return self.response


        


