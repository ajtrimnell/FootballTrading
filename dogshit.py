import requests
import json


# bigJsonList = []
''' For database and api'''
# def getTeamIds(leagueId, season, bigJsonList):
#     url = "https://api-football-v1.p.rapidapi.com/v3/teams"

#     querystring = {"league":leagueId,"season":season}

#     headers = {
#         "X-RapidAPI-Key": "fc14be64fbmshba994557bc79feep15806fjsn401a0940a28f",
#         "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring).json()

#     result = response.get('response')
    
#     teamsInLeagueList = []
#     for r in result:
#         # print(r.get('team', {}).get('name'))
#         teamsInLeagueList.append(r.get('team', {}).get('name'))
   
#     jsonObject = {
#         'model': 'backend.TeamsLeagueYear',
#         'fields': {
#             'season': season,
#             'leagueId': leagueId,
#             'teamsInLeague': teamsInLeagueList
#         }
#     }
#     print(season)
#     bigJsonList.append(jsonObject)

#     return bigJsonList
    


'''For direct json file saved on server'''
def getTeamIds(leagueId, season):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"

    querystring = {"league":leagueId,"season":season}

    headers = {
        "X-RapidAPI-Key": "fc14be64fbmshba994557bc79feep15806fjsn401a0940a28f",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()
    result = response.get('response')
    print('length = ', len(result))
    if len(result) == 0:
        return 'No data available'

    sortingList = []
    for value in result:
        sortingList.append(value.get("team", {}).get("name"))
    sortingList = sorted(sortingList)

    jsonString = "{"
    for i in sortingList:
        for r in result:
            if r.get("team", {}).get("name") == i:
                if i == sortingList[-1]:
                   jsonString = jsonString + '"' + i + '"' + ': ' + '"' + str(r.get("team", {}).get("id")) + '"' + '}'
                else:
                    jsonString = jsonString + '"' + i + '"' + ':' + '"' + str(r.get("team", {}).get("id")) + '"' + ', '
                break
            else:
                continue

    

    return json.loads(jsonString)


leaguesList = [39,40,46,45,47,48,43,41,42]
leaguesList = [43]
seasonsList = [2010, 2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2023]
seasonsList = [2023]

for season in seasonsList:
    bigJsonObject = {}
    
    bigJsonObject[season] = {}
    for league in leaguesList:
        jsonObject = getTeamIds(league, season)
        bigJsonObject[season][league] = jsonObject

    with open(f"Season{season}TeamsWithTeamId.json", "w") as outfile:
        json.dump(bigJsonObject, outfile, indent=4,  separators=(',',':')) 

       
    
    
    