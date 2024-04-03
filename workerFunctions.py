from datetime import datetime


# leagues = [39,40,41,61,78,135,140,141,144,88,141,136,62,79,94,188,113,207,119,307,253,71,128]

''' Scores from Rapid Api'''
def workerFunctionX(CallRapidApi, today, matchObjectsList, betAngelApiObject, leagues):
    
    betfairInPlayStatus(betAngelApiObject, matchObjectsList)
    # Call Rapid Api to get the current goals for each team and update the match objects.
    # Rapid Api event id is used as the identifier to find the correct match object.
    for league in leagues:
        result = CallRapidApi(today, league, '2023').inplayMatches()['response']
        for i in range(0, len(result)):
            rapidApiEventId = result[i]['fixture']['id']
            for match in matchObjectsList:
                if match.rapidApiId == rapidApiEventId:
                    match.matchScoreList.append(((datetime.now().replace(microsecond=0), result[i]['goals']['home'], result[i]['goals']['away'])))
                    match.matchStatus = result[i]['fixture']['status']['short']
                    
                    homeGoals = result[i]['goals']['home']
                    awayGoals = result[i]['goals']['away']
                    goalCount = int(homeGoals) + int(awayGoals)
                    
                    match.homeGoals = homeGoals
                    match.awayGoals = awayGoals
                    match.goalCount = goalCount
                    
                    if len(match.homeGoalsTimes) + len(match.awayGoalsTimes) != goalCount:
                        getGoalTimes(match, result[i]['events'])
                    break
    return 0


def getGoalTimes(match, result):
    for event in result:
        if event['type'] == "Goal"  and event['detail'] != "Missed Penalty":
            if match.homeTeam == event['team']['name']:
                goalTimesDict = match.goalTimesDict.get(f'{match.homeTeam}')
                minOfGoal = event['time']['elapsed']
                if minOfGoal in goalTimesDict:
                    continue
                else:
                    match.goalTimesDict.get(f'{match.homeTeam}').append(minOfGoal)
                    continue
                
            if match.awayTeam == event['team']['name']:
                goalTimesDict = match.goalTimesDict.get(f'{match.awayTeam}')
                minOfGoal = event['time']['elapsed']
                if minOfGoal in goalTimesDict:
                    continue
                else:
                    match.goalTimesDict.get(f'{match.awayTeam}').append(minOfGoal)
                    continue
    return
                
    
def betfairInPlayStatus(betAngelApiObject, matchObjectsList):
    apiCallResult = betAngelApiObject.markets()
    for result in apiCallResult:
        for match in matchObjectsList:
            if result['eventId'] == match.eventId:
                match.isInPlay = result['inPlay']
                print(match.isInPlay, match.fixture)
                break
    return