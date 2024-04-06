import pandas as pd
import json

class MatchPrices:

    def __init__(self, now, betAngelApiObject, matchObjectsList):
        self.latestOdds = betAngelApiObject.marketPrices()
        self.now = now

        ''' Check if the market has finished and is now closed'''
        def currentMatchOdds(self):
            for odds in self.latestOdds['result']['markets']:
                for match in matchObjectsList:               
                    if match.id == odds.get('id') and match.isInPlay == True: 
                        MatchPrices.updateMatchObject(match)
                        MatchPrices.pricesMatchOdds(self, match, odds)
                        MatchPrices.dataframeToCsv(self, match) 
                        break
                    else:
                        continue
                    
        currentMatchOdds(self)
        
            
    def pricesMatchOdds(self, match, odds):
        self.dfToAppend = pd.DataFrame([[self.now, match.rowIndex, 
                            odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                            odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                            odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                            odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                            odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                            odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                            columns=['matchOddsTime', 'rowIndex', 'homeBackPrice', 'homeLayPrice', 'awayBackPrice', 'awayLayPrice', 'drawBackPrice', 'drawLayPrice'])

        match.prices = pd.concat([match.prices, self.dfToAppend])
        match.rowIndex += 1
        return 
  
    def dataframeToCsv(self, match):
        self.dfToAppend.to_csv(f'./tempFiles/{match.fixture}_prices.csv', mode='a', header=False, index=False)
        
    ''' Update Match object with Rapid Api data - scores, status, goals times '''
    def updateMatchObject(match):
        
        try:
            with open(f'C:/dev/Python/betfairData/rapidApiDataCsvs/{match.fixture}.json', 'r') as file:
                content = json.load(file) 

                match.matchStatus = content['matchStatus']
                match.homeGoals = content['homeGoals']
                match.awayGoals = content['awayGoals']
                match.homeGoalsList = content['homeGoalsList']
                match.awayGoalsList = content['awayGoalsList']
                match.goalCount = content['goalCount']
            
                file.close()

        except FileNotFoundError:
            return


class MatchOddsPlusOne:
    
    def __init__(self, now, betAngelApiObject, matchObjectsList):
        self.plusOneMarkets = betAngelApiObject.plusOneMarkets()
        self.latestOddsPlusOne = betAngelApiObject.plusOneMarketPrices()
        self.now = now
        
        def marketChanges(self):
            for match in matchObjectsList:
                if match.plusOneToHomeId == None and match.plusOneToHomeId == None:
                    MatchOddsPlusOne.matchMarketIds(self, matchObjectsList)
        
        def currentMatchOddsPlusOne(self):
            for odds in self.latestOddsPlusOne:
                for match in matchObjectsList:
                    if match.plusOneToHomeId == odds.get('id') and match.isInPlay == True: 
                        pricesHomeTeamPlusOne(match, odds, match.homeTeam)
                        break
                    if match.plusOneToAwayId == odds.get('id') and match.isInPlay == True: 
                        pricesAwayTeamPlusOne(match, odds, match.awayTeam)
                        break        
        
        def pricesHomeTeamPlusOne(match, odds, homeTeam):
            dataframeToAppend(match, odds, homeTeam)
            return
        
        def pricesAwayTeamPlusOne(match, odds, AwayTeam):
            dataframeToAppend(match, odds, AwayTeam)
            return
        
        def dataframeToAppend(match, odds, team):
            if team == match.homeTeam:
                match.pricesPlusOneToHome = match.pricesPlusOneToHome._append(pd.DataFrame([[match.rowIndex, self.now, 
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                    columns=['rowIndex', 'matchOddsTime', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
                                    ),ignore_index = True)
            else:
                match.pricesPlusOneToAway = match.pricesPlusOneToAway._append(pd.DataFrame([[match.rowIndex, self.now, 
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                    odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]],
                                    columns=['rowIndex', 'matchOddsTime', f'{match.awayTeam}_back', f'{match.awayTeam}_lay', f'{match.homeTeam}_back', f'{match.homeTeam}_lay', 'drawBackPrice', 'drawLayPrice'],
                                    ),ignore_index = True)
            
            self.dfToAppend = pd.DataFrame([[match.rowIndex, self.now, 
                                odds.get('selections', {})[0].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[0].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[1].get('instances')[0].get('values')[1].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[0].get('v'),
                                odds.get('selections', {})[2].get('instances')[0].get('values')[1].get('v')]])
                                
            MatchOddsPlusOne.dataframeToCsv(self, match, team) 
            
        marketChanges(self)
        currentMatchOddsPlusOne(self)
    
    def matchMarketIds(self, matchObjectsList):
            for market in self.plusOneMarkets:
                for match in matchObjectsList:
                    if market['eventId'] == match.eventId:
                        MatchOddsPlusOne.assignMarketIds(market, match)
                        
    def splitMarketName(market):
        name = market['name'].split(' - ')[1].replace(' +1', '')
        return name
    
    # Assign the market ids of the plus one markets to the 'plusOneToHomeId' and 'plusOneToAwayId' properties in the match object.
    def assignMarketIds(market, match):
        name = MatchOddsPlusOne.splitMarketName(market).lower()
        if name == match.homeTeam.lower():
            match.plusOneToHomeId = market['id']
            return
        if name == match.awayTeam.lower():
            match.plusOneToAwayId = market['id']
            return
    
    def dataframeToCsv(self, match, team):
        self.dfToAppend.to_csv(f'./plusOneMarkets/{match.fixture}_{team}_plus_one.csv', mode='a', header=False, index=False)       