import numpy as np
import os
import json
import pandas as pd
import math
from statistics import mean 

# import yfinance as yf
import matplotlib.pyplot as plt
import csv

class Match:
    
    def __init__(self, match, homeXg, awayXg):
        
        self.match = match
        self.homeXg = homeXg
        self.awayXg = awayXg
        
        self.homeBack = []
        self.homeLay = []
        
        self.awayBack = []
        self.awayLay = []
        
        self.betPlaced = False
        self.positionExited = False
        
    def printData(self):
        print(self.match, self.homeXg, self.awayXg)


def getFile():
    
    totalProfit = 0
    for filename in os.listdir('C:/dev/Python/betfairData/formatted'): 
        
        # if filename != '190823__Bolton v Wigan - Match Odds.csv - formatted.csv':
        #     continue
        
        getXg = getExpectedGoals(filename)
        if getXg == 1:
            continue

        f = open(f'C:/dev/Python/betfairData/formatted/{filename}', 'r')
        content = f.read() 
        content = content.split('\n')

        for row in range(0, len(content)):
            content[row] = content[row].split(',')
            if row != 0:
                for i in range(1, len(content[row])):
                    try:
                        content[row][i] = float(content[row][i])
                    except (ValueError, IndexError, TypeError):
                        try:
                            del content[row][i]
                        except IndexError:
                            continue


        match = filename.split(' - ')
        match = match[0].split('__')
        
        df = pd.DataFrame(content[10:-1])
        
        match = Match(match, getXg[0], getXg[1])
        match.homeBack = df.iloc[:,3]
        match.homeLay = df.iloc[:,4]
        match.awayBack = df.iloc[:,5]
        match.awayLay = df.iloc[:,6]
        
        # createPlot(match.awayBack)
        # return
        try:
            totalProfit += loopThroughIntervals(match, getXg)
        except TypeError:
            print(match.match, getXg)
    print(totalProfit)

        

def loopThroughIntervals(match, getXg):
    
    profit = 0
    # 1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 28, 32, 36 mins
    # intervalList = [60,120,240,360,480,600,720,960,1200,1440,1680,1920,2180]
    # intervalList = [360,480,600,720,960,1200]
    intervalList = [360,480,600,720,960,1200]
    
    for i in intervalList:
        if match.betPlaced == True:
           
            return profit
        
        x1 = rateOfChangeCalcs(getXg, i/60, i/60, match)
        x2 = rateOfChange(x1[0], x1[1], x1[2], x1[3], x1[4], x1[5], x1[6])
        
        if x2 != False:
            for j in intervalList:  
                if match.positionExited == True:
                    return profit
                profit = layBetPlaced(x2[0], x2[1], x2[2], x2[3], j/60)   

    return profit


def createPlot(match):
    
    intervalList = [360,480,600,720,960,1200]
    
    for i in intervalList:
        plt.clf()
        # Rolling average and standard deviation
        movingAverage = match.rolling(window=i).mean()        
        oneStandardDev = match.rolling(window=i).std()
        # Upper and lower bollinger bands
        upperBand = movingAverage + 2 * oneStandardDev
        lowerBand = movingAverage - 2 * oneStandardDev
        # One standard deviation
        upperStdDev  = movingAverage + 1 * oneStandardDev
        lowerStdDev = movingAverage - 1 * oneStandardDev  
           
        xAxis = range(0, len(upperBand))    
        plt.plot(xAxis, match, xAxis, upperBand, xAxis, lowerBand, xAxis, movingAverage, xAxis, upperStdDev, 'b--', xAxis, lowerStdDev, 'b--', linewidth=.5)
        
        ax = plt.gca()
        ax.set_xlim([0,2700])
        ax.set_ylim([3,4.5])
        
        plt.savefig(f'291223__Burton Albion v Shrewsbury - Shewsbury-{i}', dpi=1200)
        # plt.show()
    return
        
   
   
def rateOfChangeCalcs(xg, periodMins, min, match):
    
    homeXg = xg[0]
    awayXg = xg[1]
    
    homeOdds = match.homeBack
    awayOdds = match.awayBack
   
    start = min - periodMins
    if start < 0:
        return ('Period not valid')
    
    minToSeconds = min * 60
    startToSeconds = start * 60
    # print(match.match)
    homePriceAtStart = homeOdds[startToSeconds]
    homePriceAtEnd = homeOdds[minToSeconds]
    
    homeXgForPeriod = xGRemaining(homeXg, start)  - xGRemaining(homeXg, min)
    awayXgForPeriod = xGRemaining(awayXg, start)  - xGRemaining(awayXg, min) 

    loss = homeXgForPeriod * -0.65
    gain = awayXgForPeriod * 0.5

    totalLoss = gain + loss
    
    breakEven = totalLoss
    initialPrice = homePriceAtStart
    price = homePriceAtStart # Of period being measured
    
    return match, totalLoss, initialPrice, breakEven, price, min, periodMins
    rateOfChange(match, totalLoss, initialPrice, breakEven, price, min, periodMins)
    
    # return
 
 
def getTotalLoss(match, start, min):
    
    homeXg = match.homeXg
    awayXg = match.awayXg
    
    homeXgForPeriod = xGRemaining(homeXg, start)  - xGRemaining(homeXg, min)
    awayXgForPeriod = xGRemaining(awayXg, start)  - xGRemaining(awayXg, min) 

    loss = homeXgForPeriod * -0.65
    gain = awayXgForPeriod * 0.5

    totalLoss = gain + loss
    
    return totalLoss
   
    
def rateOfChange(match, totalLoss, initialPrice, breakEven, price, min, periodMins):

    i = 0
    
    bollingerBandHome = bollingerBands(match.homeBack, int(periodMins*60))
    upperBand = bollingerBandHome[0]
    lowerBand = bollingerBandHome[1]
    movingAverage = bollingerBandHome[2]
    
    bollingerBandAway = bollingerBands(match.homeBack, int(periodMins*60))
    upperBandAway = bollingerBandAway[0]
    lowerBandAway = bollingerBandAway[1]
    movingAverageAway = bollingerBandAway[2]
    
    while breakEven < 0:   
        homeOdds = mean(match.homeBack[int((min-1)*60):int(min*60)])
        awayOdds = mean(match.awayBack[int((min-1)*60):int(min*60)])

        # homeOddsArray = match.homeBack
        price += 0.01
        breakEven = totalLoss + (((price-1) - (initialPrice-1)) / price)
        
        # Check for price spikes
        rangeValue = 10
        if periodMins < 10:
            rangeValue = int(periodMins)
            
        for s in range(0, rangeValue*60):
            spikeTest = homeOdds*.85
            if spikeTest > match.homeBack[min*60-s] or spikeTest > match.homeBack[15]:
                return False
            if match.homeBack[min*60-s] < movingAverage[int(min*60-s)]:
                return False

        if breakEven > 0 and homeOdds - price >= 0:
            # and i < min:
            homeLastMinAverage = mean(match.homeBack[int((min-1)*60): int(min*60)])
            
            # Gradient of moving average price of away team
            for second in range(0, 60):
                movingAverageAwayGradient = (movingAverageAway[(int(second+(min-1)*60))] - movingAverageAway[(int(second+(min-1)*60)-int(periodMins)*60)]) / ((int(second+(min-1)*60) - (int(second+(min-1)*60)-(int(periodMins)*60)))) * 60
            if homeLastMinAverage < upperBand[int(min*60)] and homeLastMinAverage <= 2.5 and homeLastMinAverage > 2 and movingAverageAwayGradient < 0: 
                #   
                match.betPlaced = True
                homeBetPlacedAt = homeOdds+0.01
                awayBetPlacedAt = awayOdds-0.01
                with open('results.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([match.match, 'Home lay placed at ', homeBetPlacedAt, 'Away back placed at ', awayBetPlacedAt, 'minute ', min])
                print('bet placed') 
                return min, homeBetPlacedAt, awayBetPlacedAt, match            
        i += 1
        
    return False
 
    
def layBetPlaced(min, homeLayPlacedAt, awayBackPlacedAt, match, periodMins):
    # Recalculate for interval
    bollingerBand = bollingerBands(match.homeBack, int(periodMins*60))
    upperBand = bollingerBand[0]
    lowerBand = bollingerBand[1]
    movingAverage = bollingerBand[2]
    
    
    startMin = min
    price = homeLayPlacedAt
    
    ''''''
    homeXg = match.homeXg
    awayXg = match.awayXg
    
    homeOdds = match.homeBack
    awayOdds = match.awayBack
   
    start = min - 4
    if start < 0:
        return ('Period not valid')
    
    minToSeconds = min * 60
    startToSeconds = start * 60
    
    homePriceAtStart = homeOdds[startToSeconds]
    homePriceAtEnd = homeOdds[minToSeconds]
    
    homeXgForPeriod = xGRemaining(homeXg, start)  - xGRemaining(homeXg, min)
    awayXgForPeriod = xGRemaining(awayXg, start)  - xGRemaining(awayXg, min) 

    loss = homeXgForPeriod * -0.55
    gain = awayXgForPeriod * 0.5

    totalLoss = gain + loss
    
    # breakEven = totalLoss
    initialPrice = homePriceAtStart
    price = homePriceAtStart 
    ''''''
       
    if match.betPlaced == True:
        # print('betPlacedAt', betPlacedAt)
        price += 0.01  
        i = 0   
        minBetPlaced = int(min)
        # upperBand = bollingerBands(match.homeBack, 4*60)[0]
        min += 4
        for m in range(minBetPlaced, 45):

        # while breakEven < 0:   
            # print(m)
            ''' Check for goals'''
            
            for s in range(0, 60):
                # Check for away goal
                if (match.awayBack[s+(m-2)*60])*0.85 > match.awayBack[s+m*60] and (match.homeBack[(min-2)*60])*1.15 < match.homeBack[min*60] or (match.awayBack[s+(m-4)*60])*0.85 > match.awayBack[s+m*60] and (match.homeBack[(min-4)*60])*1.15 < match.homeBack[min*60]:
                    if (match.awayBack[min*60] / match.awayLay[min*60]) > 0.95:
                        profit = round(((match.homeBack[min*60]-1) - (homeLayPlacedAt-1)) / match.homeBack[min*60], 4)
                        
                        awayProfit = round(((awayBackPlacedAt-1) - (match.awayBack[min*60]-1)) / match.awayBack[min*60], 4)*0.25
                        with open('results.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([match.match, f'Exit position at minute {min} on away goal at odds {match.homeBack[min*60]} - profit =', profit, homeLayPlacedAt, 'awayProfit', awayProfit, 'minute =', minBetPlaced])
                            writer.writerow(['Odds spread: ',match.match, match.awayBack[min*60], match.awayLay[min*60]])
                        # print(f'Exit position at minute {min} on away goal at odds {match.homeBack[min*60]} - profit =', profit)
                        match.positionExited = True               
                        return profit+awayProfit
                    
                # Check for home goal
                if (match.homeBack[s+(m-3)*60])*0.75 > match.homeBack[s+m*60] and (match.awayBack[(min-3)*60])*1.15 < match.awayBack[min*60]:
                    if (match.homeBack[min*60] / match.homeLay[min*60]) > 0.95:
                        profit = round(((match.homeBack[min*60]-1) - (homeLayPlacedAt-1)) / match.homeBack[min*60], 4)
                        awayProfit = round(((awayBackPlacedAt-1) - (match.awayBack[min*60]-1)) / match.awayBack[min*60], 4)*0.25
                        with open('results.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([match.match, f'Exit position at minute {min} on home goal at odds {match.homeBack[min*60]} - profit =', profit, homeLayPlacedAt, 'awayProfit', awayProfit, 'minute =', minBetPlaced])
                            writer.writerow(['Odds spread: ', match.match, match.awayBack[min*60], match.awayLay[min*60]]) 
                        match.positionExited = True
                        return profit+awayProfit

                # Check for odds returning to value
                movingAverageGradient = (movingAverage[(int(s+m*60))] - movingAverage[(int(s+m*60)-int(periodMins)*60)]) / ((int(s+m*60) - (int(s+m*60)-(int(periodMins)*60)))) * 60
                # print(movingAverageGradient)
                # if match.homeBack[s+m*60] < movingAverage[int(s+m*60)] and (match.homeBack[s+(m-5)*60])*1.2 > match.homeBack[s+m*60] and movingAverageGradient < 0.01:
                    
                #     # print(match.match, (match.homeBack[s+(m-5)*60])*1.2, match.homeBack[s+m*60])
                #     profit = round(((match.homeBack[min*60]-1) - (betPlacedAt-1)) / match.homeBack[min*60], 4)
                    
                #     with open('results.csv', 'a', newline='') as file:
                #         writer = csv.writer(file)
                #         writer.writerow([match.match, f'Exit position at minute {min} at level odds {match.homeBack[min*60]} - profit =', profit, betPlacedAt, 'minute =', minBetPlaced])

                #     match.positionExited = True
                #     return profit
                
                if movingAverageGradient < 0.01:
                    profit = round(((match.homeBack[min*60]-1) - (homeLayPlacedAt-1)) / match.homeBack[min*60], 4)
                    awayProfit = round(((awayBackPlacedAt-1) - (match.awayBack[min*60]-1)) / match.awayBack[min*60], 4)*0.25
                    with open('results.csv', 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([match.match, f'Exit position at minute {min} at level odds {match.homeBack[min*60]} - profit =', profit, homeLayPlacedAt, 'awayProfit', awayProfit, 'minute =', minBetPlaced])

                    match.positionExited = True
                    return profit+awayProfit

                
               
                # print((movingAverage[(int(20*60))], movingAverage[int(14*60)]), ((int(20*60), (int(14*60)))))
                # print((movingAverage[(int(20*60))] - movingAverage[int(14*60)]) / ((int(20*60) - (int(14*60))))*60)

                # homeOdds = match.homeBack[min*60]
                # price += 0.01
                # breakEven = totalLoss + (((price-1) - (initialPrice-1)) / price)
                
                # homeLastMinAverage = mean(match.homeBack[int((min-1)*60): int(min*60)])
                # homeLastMinAverage1 = mean(match.homeBack[int((min-2)*60): int(min*60)])
                # homeLastMinAverage2 = mean(match.homeBack[int((min-3)*60): int(min*60)])
                # homeLastMinAverage3 = mean(match.homeBack[int((min-4)*60): int(min*60)])
                # homeLastMinAverage4 = mean(match.homeBack[int((min-5)*60): int(min*60)])
                # homeLastMinAverage5 = mean(match.homeBack[int((min-6)*60): int(min*60)])

                # for s in range(0, int(periodMins*60)):
                #     if match.homeBack[min*60-s] < movingAverage[int(min*60-s)] and (match.homeBack[(min-1)*60])*0.85 > match.homeBack[min*60] and (match.awayBack[min*60] / match.awayLay[min*60]) > 0.95:
                #         print(match.homeBack[min*60-s], movingAverage[int(min*60-s)], min)
                #         if homeLastMinAverage1 > homeLastMinAverage and homeLastMinAverage2 > homeLastMinAverage and homeLastMinAverage3 > homeLastMinAverage and homeLastMinAverage4 > homeLastMinAverage and homeLastMinAverage5 > homeLastMinAverage:
                #             print()
                #             profit = round(((match.homeBack[min*60]-1) - (betPlacedAt-1)) / match.homeBack[min*60], 4)
                #             with open('results.csv', 'a', newline='') as file:
                #                 writer = csv.writer(file)
                #                 writer.writerow([match.match, f'Exit position at minute {min} on odd leveling - profit =', profit, 'Bet placed at =', betPlacedAt, 'minute =', minBetPlaced])
                #             return
            
            
            
            
                
                # if breakEven > 0 and homeOdds - price >= 0:
                #     # while homeOdds - price >= 0:
                        
                #     totalLoss = getTotalLoss(match, startMin, min)
                #     minToSeconds = int(min*60)
                    
                #     # https://numpy.org/doc/stable/reference/generated/numpy.max.html
                #     # upperBandMax = np.max(upperBand[0:minToSeconds], where=~np.isnan(upperBand[0:minToSeconds]), initial=-1)

                #     homeOdds = match.homeBack[min*60]
                #     price += 0.01
                #     breakEven = totalLoss + (((price-1) - (initialPrice-1)) / price)

                #     # Exit the position if the odds are adjusting to value
                #     if breakEven < 0.01:
                        
                #         profit = round(((price-1) - (initialPrice-1)) / price, 4)
                        
                #         with open('results.csv', 'a', newline='') as file:
                #             writer = csv.writer(file)
                #             writer.writerow([match.match, f'Exit position at minute {min} on breakeven number - profit =', profit, 'Bet placed at =', betPlacedAt, 'minute =', minBetPlaced])
                        
                #         match.betPlaced = False
                #         print(f'Exit position at minute {min} on breakeven number - profit =', profit)
                #         return
                
                
                if min*60 > 2699:
                    profit = round(((match.homeBack[min*60]-1) - (homeLayPlacedAt-1)) / match.homeBack[min*60], 4)
                    awayProfit = round(((awayBackPlacedAt-1) - (match.awayBack[min*60]-1)) / match.awayBack[min*60], 4)*0.25
                    with open('results.csv', 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([match.match, f'Exit position at halftime {min} on breakeven number - profit = ', profit, 'Bet placed at =', homeLayPlacedAt, 'awayProfit', awayProfit, 'minute =', minBetPlaced])
                    
                    match.positionExited = True
                    print('Half time')  
                    return profit+awayProfit

            i += 1
            min += 1  
        
    return
    
    
  
  
def xGRemaining(xg, min):
    return ((1-(1/95*min))**.84) * xg
 
 
def bollingerBands(match, x): 
    # plt.clf() 
    # Rolling average and standard deviation
  
    movingAverage = match.rolling(window=x).mean()        
    oneStandardDev = match.rolling(window=x).std()
    
    stdAverage = (oneStandardDev) + movingAverage
    stdAverageNp = np.array(stdAverage)
    # print(match)
    # lst1 = []
    # for i in range(0, len(np.asarray(match[0:2700]))):
        
    #     lst1.append(match[i] - movingAverage[i])
   
    # plt.plot(lst1)
    # # plt.plot(match.rolling(window=x))
    # plt.show()
    # Upper and lower bollinger bands
    upperBand = np.array(movingAverage + 2 * oneStandardDev)
    lowerBand = movingAverage - 2 * oneStandardDev
    # One standard deviation
    upperStdDev  = movingAverage + 1 * oneStandardDev
    lowerStdDev = movingAverage - 1 * oneStandardDev 

    return upperBand, lowerBand, stdAverageNp
    
    

        
    

def checkPlusOneMarkets(filename):
    match = filename.split(' - ')   
    matchTeams = match[0].split('__')
    matchTeams = matchTeams[1].split(' v ')
    try:
        open(f'G:/My Drive/match_odds_data_gathering_plus_one/{match[0]} - {matchTeams[0]} +1.csv', 'r')  
        return True
    except FileNotFoundError:
        return False
    
    
     
def getExpectedGoals(filename):

    match = filename.split(' - ')
    match = match[0].split('__')

    try:
        f = open(f'G:/My Drive/expected_goals_data_gathering/{match[0]}_XG__{match[1]} - Correct Score.csv', 'r')
      
    except FileNotFoundError:
        return 1

    content = f.read() 
    content = content.split('\n')
    content[1] = content[1].split(',')

    if content[1][7] == 'Total goals':
        return round(float(content[1][10]), 2), round(float(content[1][6]), 2)
    else:
        return round(float(content[1][8]), 2), round(float(content[1][6]), 2)
    

def rsi(match, period):
    
    period = 480
    prices = match.homeBack
    
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    rsi = rsi[ :2700]
   
    aAxis = range(0, len(rsi))
    
    plt.plot(aAxis, rsi)
    plt.show()
    
    
    return rsi
    
    
    

getFile()