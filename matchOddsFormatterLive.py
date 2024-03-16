import pandas as pd
import os
import numpy as np

from minutesForDf import minutes_list_for_df
from get_xg import xg_remaining

# import psycopg2
# from psycopg2 import Error

import json
from datetime import datetime

import timeit

runners_list = []
markets = 0
file_dict = {}

def update_file_dict(file_dict):  
    with open("file_dict.json", "w") as outfile:
        json.dump(file_dict, outfile)
        
def update_start_time_dict(start_time_dict):  
        with open("start_time_dict.json", "w") as outfile:
            json.dump(start_time_dict, outfile)
        
# def update_fixtures():
    
#     try:
#         conn = psycopg2.connect(
#             database="bet_angel",
#             user="postgres",
#             password="password",
#             host="44.216.250.228"
#             )
    
#         cursor = conn.cursor()
        
#         cursor.execute("""INSERT INTO fixtures(fixture)
#                         VALUES (%s);""",
#                         (
#                             '060823__Sunderland v Ipswich',                     
#                         ))
#         conn.commit()

#     except (Exception, Error) as error:
#         print("ERROR!!!!!", error)
#         return


# def update_match_odds(df_2, filename):
#     start, stop = 0, 0
#     start = timeit.default_timer()
#     with open('fixture_id_dict.json') as j:
#         fixture_id_dict = json.load(j)

#     match = filename.split(' - ')
#     match = match[0].split('__')
#     print(match)
#     # insert fixture_id column
#     df_2.insert(loc=0, column='fixture_id', value=int(fixture_id_dict.get(match[1])))
    
#     try:
#         conn = psycopg2.connect(
#                 database="bet_angel",
#                 user="postgres",
#                 password="password",
#                 host="44.216.250.228"
#                 )
        
#         conn.autocommit = True
        
#         cursor = conn.cursor()
        
#         values = list(zip(*map(df_2.get, df_2)))

#         # cursor.mogrify() to insert multiple values
#         args = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", i).decode('utf-8')
#                         for i in values)
#         # executing the sql statement
#         cursor.execute("INSERT INTO match_odds VALUES " + (args))
        
#         # committing changes
#         conn.commit()
        
#         # closing connection
#         conn.close()
#         stop = timeit.default_timer()
#         print('TIME: ', stop - start)
        
#     except (Exception, Error) as error:
#         print("ERROR!!!!!", error)
#         return
        

def group_by_second():
    
    with open('file_dict.json') as j:
        file_dict = json.load(j)
        
    with open('start_time_dict.json') as j:
        start_time_dict = json.load(j)
    
    time_interval_split = 1/60    
    for filename in os.listdir('C:/Users/AJTri/OneDrive/Desktop/match_odds_data_csv'):   
    # for filename in os.listdir('D:/Football Match Odds Data'):    
        
        print('#### ', filename)
        ### create a pandas dataframe from the opened csv file ###
        f = open(f'C:/Users/AJTri/OneDrive/Desktop/match_odds_data_csv/{filename}', 'r')
        # f = open(f'D:/Football Match Odds Data/{filename}', 'r')
        ### read the content from the csv file and split content string into list at each new line ### 
        content = f.read() 
        content = content.split('\n')

        row_count = sum(1 for row in content)
        csv_exists = 0
        
        # 'try' will only work if the match csv has already been read. A Keyerror will occur if it hasn't, and a dictionary
        # will then be created
        try:      
            start = file_dict[f'{filename}']
            
            del content[0:start]
            # check to see if the match is still in play - if it has ended then 'start == row_count'
            if start != row_count:
                for row in range(0, len(content)):
                    content[row] = content[row].split(',')
                file_dict[f'{filename}'] = row_count
                update_file_dict(file_dict)
                csv_exists = 1
                xg_remain = xg_remaining(filename)
            else:
                print('Match ended')
                continue
            
        except KeyError:       
            xg_remain = xg_remaining(filename)
            if xg_remain == 1:
                continue
            
            for row in range(0, len(content)):
                content[row] = content[row].split(',')
                
            start_time = content[1][0]    
            
            file_dict[f'{filename}'] = row_count
            update_file_dict(file_dict)
            
            start_time_dict[f'{filename}'] = start_time
            update_start_time_dict(start_time_dict)
            

        match = filename.split(' - ')
        match = match[0].split('__')

        ### create dataframe from content, skipping the first row with the headers ###
        df = pd.DataFrame(content[1:-2])
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
        df_values_only = df[[0,'min',6,8,18,20,30,32,10,22,34]]
        
        

        # group/ collate rows by second, taking the mean of the values
        df_2 = (df_values_only.groupby([pd.Grouper(key=0, freq=f'{time_interval_split}min')]).mean()).round(2)
 
        
        ### MINUTE COUNTER ###
        ### adjust the 'min' column to give the current minute since kickoff ###
        if csv_exists == 1:  
            formatted_df = open(f'C:/Users/AJTri/OneDrive/Desktop/formatting_test/{filename} - formatted.csv', 'r')
            content_df = formatted_df.read() 
            content_df = content_df.split('\n')
            row_count_df = sum(1 for row in content_df)
            formatted_df.close()
        
        if csv_exists == 0:
            df_2['min'] = minutes_list_for_df[0:len(df_2)]
        else:
            df_2['min'] = minutes_list_for_df[row_count_df-2:row_count_df+len(df_2)-2]

        cols = [df_2.columns]
        
        for i in cols:
            df.drop(df[i], axis=1, inplace=True)
            
        ### CURRENT EXPECETED GOALS REMAINING ###  
        df_2['home_xg'] = round((df_2['min'].map(xg_remain[0])), 3)
        df_2['away_xg'] = round((df_2['min'].map(xg_remain[1])), 3)
        ### CHANGE IN EXPECTED GOALS ###
        df_2['home_xg_change'] = round((df_2['min'].map(xg_remain[4])), 3)
        df_2['away_xg_change'] = round((df_2['min'].map(xg_remain[5])), 3)
       
        # Create a seconds elapsed column
        time_elapsed = []
        date_time_column = df_2.index
        print('>>>>>>> ', start_time_dict.get(filename))
        start_point = datetime.strptime(start_time_dict.get(filename), '%d/%m/%Y %H:%M:%S.%f').replace(microsecond=0)
        
        for t in date_time_column:
            delta = (t - start_point).total_seconds()
            time_elapsed.append(delta)
       
        df_2 = df_2.fillna(method='bfill')
        
        start_length = len(df_2)
        df.pop(0)
        
        if len(df) > len(df_2):
            df.drop(df.iloc[start_length:].index, axis=0, inplace=True)
        else:
            df_2.drop(df_2.iloc[len(df):].index, axis=0, inplace=True)
      
        for d in df_2:
            df_2[d] = np.asarray(df_2[d])
            
        if csv_exists == 1:
            df_2.to_csv(f'C:/Users/AJTri/OneDrive/Desktop/formatting_test/{filename} - formatted.csv', mode='a', header=False) 
        else:
            df_2.to_csv(f'C:/Users/AJTri/OneDrive/Desktop/formatting_test/{filename} - formatted.csv') 
        
        # Inset seconds elapsed column into dataframe
        df_2.insert(loc=0, column='seconds_elapsed', value=time_elapsed)

        # update_match_odds(df_2, filename)
        
    return


group_by_second()




    