import requests
from pprint import pprint
import time
import datetime
import csv

api_token = 'F2lUNllcICReywhCwb8lSHN7NYbrAZGdrGKynstAr8w676mtPFJTuBoFtaWk'
apiUrl = f'https://api.sportmonks.com/v3/football/fixtures/date/2024-03-02?api_token={api_token}&include=scores'
response = (requests.get(apiUrl, headers = {'Content-Type': 'application/json'})).json()

dataToWrite = response.get('data')[0].get('name'), response.get('data')[0].get('state_id'), datetime.datetime.now()

# time.sleep(420)

while True:
    time.sleep(15)
    
    response = (requests.get(apiUrl, headers = {'Content-Type': 'application/json'})).json()
    
    for r in range(0, len(response)):
        dataToWrite = response.get('data')[r].get('name'), response.get('data')[r].get('state_id'), datetime.datetime.now()
        
        with open('sportmonksTest2.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(dataToWrite)
