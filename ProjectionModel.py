# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 01:08:25 2018

@author: Durugshan
"""

import pandas as pd
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

# import the saved final player values
zScoreData = pd.read_csv("FinalPlayerValues.csv")

# We only care about columns with Z Scores for x values in model
colstoX = [cols for cols in zScoreData.columns if cols.upper()[-1:] == 'Z']

# Set the x and y data to the zScores and league value respectively
xData = zScoreData[colstoX].copy()
yData = zScoreData['LeagueValue']

# fill any nan values
xData = xData.fillna(0)

# create training and testing vars
X_train, X_test, y_train, y_test = train_test_split(xData, yData, test_size=0.2)

# fit a model
lm = linear_model.LinearRegression()

# run predictions
model = lm.fit(X_train, y_train)
predictions = lm.predict(X_test)

# plot the data
plt.style.use('fivethirtyeight')

## The line / model
plt.scatter(y_test, predictions)
plt.xlabel('True Values')
plt.ylabel('Predictions')

# the R2, coeffecients and intercept
lm.score(xData, yData)
lm.coef_
lm.intercept_