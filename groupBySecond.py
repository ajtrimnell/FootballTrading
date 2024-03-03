import numpy as np
import os
import pandas as pd
import math
import json


def group_by_second():
    
    i = 0
    time_interval_split = 1/60    
    for filename in os.listdir('G:/My Drive/match_odds_data_gathering'): 
        # filename = '240224__Man Utd v Fulham - Match Odds.csv'

        if os.path.exists(f'C:/dev/Python/betfairData/formatted/{filename} - formatted.csv'):
            print('exists')
            continue

        try:
            getXg = getExpectedGoals(filename)
            if getXg == 1:
                continue
                 
            ### create a pandas dataframe from the opened csv file ###
            f = open(f'G:/My Drive/match_odds_data_gathering/{filename}', 'r')
            ### read the content from the csv file and split content string into list at each new line ### 
            content = f.read() 
            content = content.split('\n')

            for row in range(0, len(content)):
                content[row] = content[row].split(',')

            match = filename.split(' - ')
            match = match[0].split('__')

            ### create dataframe from content, skipping the first row with the headers ###
            df = pd.DataFrame(content[1:])
        
            ### convert the date and column to datetime format ###
            df[df.columns[0]] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
            
            df['min'] = df[0].dt.minute
            df['min'] = df['min'].astype(str)
            df['min'] = df['min'].astype(float)
            
            ### iterate through the columns of the dataframe and change all column vales to float type if possible ###
            ### ignore columns that cannot be converted ###
            for i in df:
                try:
                    df[i] = df[i].astype(float)
                except:
                    TypeError
                    continue   
            # select only the columns that have a numerical value
            df_values_only = df[[0,6,8,18,20,30,32]]
                # ,10,22,34]] # Matched volume
        
            # group/ collate rows by second, taking the mean of the values
            df_2 = (df_values_only.groupby([pd.Grouper(key=0, freq=f'{time_interval_split}min')]).mean()).round(2)

            cols = [df_2.columns]
            
            for i in cols:
                df.drop(df[i], axis=1, inplace=True)

            # Create a seconds elapsed column
            time_elapsed = []
            date_time_column = df_2.index
            start_point = date_time_column[0]
            for t in date_time_column:
                delta = (t - start_point).total_seconds()
                time_elapsed.append(delta)
        
            minsElapsed = []
            for e in time_elapsed:
                minsElapsed.append(math.floor(e/60))

            df_2 = df_2.fillna(method='bfill')
            df_2.insert(loc=0, column='seconds_elapsed', value=time_elapsed)
            df_2.insert(loc=0, column='mins_elapsed', value=minsElapsed)
            
            start_length = len(df_2)
            df.pop(0)
            
            if len(df) > len(df_2):
                df.drop(df.iloc[start_length:].index, axis=0, inplace=True)
            else:
                df_2.drop(df_2.iloc[len(df):].index, axis=0, inplace=True)

            for d in df_2:
                df_2[d] = np.asarray(df_2[d])
                        
            df_2.to_csv(f'C:/dev/Python/betfairData/formatted/{filename} - formatted.csv') 
            
        except (IndexError, ValueError):
            continue
    return


def getExpectedGoals(filename):

    match = filename.split(' - ')
    match = match[0].split('__')

    # f = open(f'C:/Users/AJTri/OneDrive/Desktop/correct_score_csv/{match[0]}_XG__{match[1]} - Correct Score.csv', 'r')
    try:
        f = open(f'G:/My Drive/expected_goals_data_gathering/{match[0]}_XG__{match[1]} - Correct Score.csv', 'r')
      
    except FileNotFoundError:
        return 1

    content = f.read() 
    content = content.split('\n')
    content[1] = content[1].split(',')

    if content[1][7] == 'Total goals':
        return content[1][6], content[1][10]
    else:
        return content[1][8], content[1][6]



group_by_second()