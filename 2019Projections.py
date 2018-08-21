# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 22:42:01 2018

@author: Durugshan
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def scrapePlayer(year):
    # url to get data
    playerStatsSource = 'https://www.basketball-reference.com/leagues/NBA_'+str(year)+'_totals.html'
    
    # opening the url
    page = urlopen(playerStatsSource)
    
    # loading it into BS
    soup = BeautifulSoup(page, "lxml")
    
    # get column headers by first column
    column_headers = [th.getText() for th in 
                      soup.find('tr').findAll('th')]
    
    # skip the first  header row
    data_rows = soup.findAll('tr')[1:] 
    
    player_data = [[td.getText() for td in data_rows[i].findAll('td')]
                for i in range(len(data_rows))]
    
    # create an empty list to hold all the data
    player_data_02 = []  
    
    # for each table row
    # create an empty list for each pick/player
    for i in range(len(data_rows)):  
        player_row = []  
    
        # for each table data element from each table row
        for td in data_rows[i].findAll('td'):        
            # get the text content and append to the player_row 
            player_row.append(td.getText())        
    
        # then append each pick/player to the player_data matrix
        player_data_02.append(player_row)
        
    finalPlayerData = pd.DataFrame(player_data, columns=column_headers[1:])
    finalPlayerData = finalPlayerData[finalPlayerData['Player'].notnull()]
    
    # put integer type columns into a list
    listIntCols = ['Age', 'G', 'GS', 'MP', 'FG', 'FGA', '3P',
           '3PA', '2P', '2PA', 'FT', 'FTA', 'ORB',
           'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
    
    # put float type columns into a list
    listFloatCols = ['FG%', '3P%', '2P%', 'eFG%', 'FT%']
    
    #change those columns in the dataframe
    for i in listIntCols:
        finalPlayerData[i] = pd.to_numeric(finalPlayerData[i], downcast = 'integer')
        
    for j in listFloatCols:
        finalPlayerData[j] = pd.to_numeric(finalPlayerData[j], downcast = 'float')
    
    finalPlayerData = finalPlayerData.sort_values('PTS', ascending = False)
    finalPlayerData = finalPlayerData.drop_duplicates('Player')
    finalPlayerData = finalPlayerData.reset_index(drop=True)
    
    return finalPlayerData

overallPlayerData = pd.DataFrame(columns = ['Player', 'Pos', 'Age', 'Tm', 'G', 
                                            'GS', 'MP', 'FG', 'FGA', 'FG%', 
                                            '3P', '3PA', '3P%', '2P', '2PA', 
                                            '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 
                                            'ORB', 'DRB', 'TRB', 'AST', 'STL', 
                                            'BLK', 'TOV', 'PF', 'PTS', 'Year'])
        
for a in range(2000, 2019):
    yearlyPlayerData = scrapePlayer(a)
    yearlyPlayerData['Year'] = a
    overallPlayerData = overallPlayerData.append(yearlyPlayerData)
