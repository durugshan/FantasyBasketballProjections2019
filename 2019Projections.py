# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 22:42:01 2018
@author: Durugshan
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

# function to scrape player data 
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
    
    #change those columns in the dataframe
    for i in listIntCols:
        finalPlayerData[i] = pd.to_numeric(finalPlayerData[i], downcast = 'integer')
        
    for i in listFloatCols:
        finalPlayerData[i] = pd.to_numeric(finalPlayerData[i], downcast = 'float')
    
    # remove any duplicates of players that played on multiple teams
    finalPlayerData = finalPlayerData.sort_values('PTS', ascending = False)
    finalPlayerData = finalPlayerData.drop_duplicates('Player')
    finalPlayerData = finalPlayerData.reset_index(drop=True)
        
    return finalPlayerData

# calculate the Z Scores for each stat
def calculateZScores(finalPlayerData):
    # create a copy of the scraped data
    finalPlayerData = finalPlayerData.copy()
    
    # adding a columns that will convert season counting stats into per game stats
    for i in listIntCols[3:]:
        finalPlayerData[str(i +'/G')] = finalPlayerData[i]/finalPlayerData['G'] 
    
    # convert the counting stats per game into zScores ((value - mean) / std)
    for i in listIntCols[3:]:
        finalPlayerData[str(i + 'Z')] = (finalPlayerData[i + '/G'] - finalPlayerData[i + '/G'].mean()) / finalPlayerData[i + '/G'].std()
    
    # convert percent stats into weighted percent
    # ((value - mean)/ std) * (attempts/total attempts)
    for i in listFloatCols:
        if i == 'eFG%':
            finalPlayerData[str('w' + i)] = ((finalPlayerData[i] - finalPlayerData[i].mean()) / finalPlayerData[i].std()) * ((finalPlayerData['FGA'] + 0.5 * finalPlayerData['3PA']) / (finalPlayerData['FGA'].sum() + 0.5 * finalPlayerData['3PA'].sum()))
        else:
            x = i[:-1] + 'A'
            finalPlayerData[str('w' + i)] = ((finalPlayerData[i] - finalPlayerData[i].mean()) / finalPlayerData[i].std()) * (finalPlayerData[x] / finalPlayerData[x].sum())
    
    # convert weighted percent stats into zScores
    for i in listFloatCols:
        finalPlayerData[str(i + 'Z')] = (finalPlayerData['w' + i] - finalPlayerData['w' + i].mean()) / finalPlayerData['w' + i].std()
    
    return finalPlayerData

# creating a copy of just ZScore columns
def ZScoreCopy(yearlyPlayerData):
    zScoreCopy = yearlyPlayerData.copy()
    
    # making a list of columns that end with Z
    colstoKeep = [cols for cols in zScoreCopy.columns if cols.upper()[-1:] == 'Z']
    
    # creating that copy
    zScoreCopy = zScoreCopy[colstoKeep]
    
    return zScoreCopy

# redistributing the zScores from -1 to 1
def ZScoreDist(zScoreCopy):
    # the columns with Z scores
    zCols = list(zScoreCopy.columns)
    
    # a dataframe with those columns
    zDist = pd.DataFrame(columns = zCols)
    
    # for those columns, include the redistributed zScore
    for i in zCols:
        # if it's a turnover, less is better so multiply by -1
        if i == 'TOVZ':
            zDist[i] = (-1) * zScoreCopy[i] / abs(zScoreCopy[i].max() - zScoreCopy[i].min())
        # for everything else, take value of zScore/abs(max-min)
        else:
            zDist[i] = zScoreCopy[i] / abs(zScoreCopy[i].max() - zScoreCopy[i].min())
            
    return zDist

# calculate the final League Value by adding the redistributed zScores
# only for relevant stats specified in league Stats
def calculateValue(finalZList, leagueStats):
    finalZList = finalZList.copy()
    finalZList['LeagueValue'] = finalZList[leagueStats].sum(axis=1)
    return finalZList

# Main

# the relevant league stats that we are interested in        
leagueStats = ['FG%', '3P', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']

# put integer type columns into a list
listIntCols = ['Age', 'G', 'GS', 'MP', 'FG', 'FGA', '3P',
       '3PA', '2P', '2PA', 'FT', 'FTA', 'ORB',
       'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

# put float type columns into a list
listFloatCols = ['FG%', '3P%', '2P%', 'eFG%', 'FT%']

# add a Z with each league stat since we're interested in zscores
for i in range(len(leagueStats)):
    leagueStats[i] = str(leagueStats[i]) + 'Z'
   
# create an ampty dataframe to store historical data
overallPlayerData = pd.DataFrame()
   
# iterate through each year specified  
for a in range(2017, 2019):
    # scrape player data for year
    yearlyPlayerData = scrapePlayer(a)
    
    # calculate the Z Scores
    yearlyPlayerDataZ = calculateZScores(yearlyPlayerData)
    
    # create a copy with just zScores
    zScoreCopy = ZScoreCopy(yearlyPlayerDataZ)
    
    #redistribute with range -1, 1
    zScoreDist = ZScoreDist(zScoreCopy)
    
    # relevant player name columns are just the first 5
    playerCols = list(yearlyPlayerData.columns[0:5])
    
    # add a year to the yearly player data
    yearlyPlayerData['Year'] = a
    
    # set up frames to combine the player data with distributed zScores
    ZListFrames = [yearlyPlayerData, zScoreDist]
    
    # combine the two
    finalZList = pd.concat(ZListFrames, axis = 1)
    
    # calculate a league value
    finalZCalculations = calculateValue(finalZList, leagueStats)
    
    # append to overall table that will have for all years specified
    overallPlayerData = overallPlayerData.append(finalZCalculations)

# save to csv
overallPlayerData.to_csv("FinalPlayerValues.csv")