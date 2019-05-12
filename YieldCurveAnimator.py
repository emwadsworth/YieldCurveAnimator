#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 00:59:26 2019
@author: edwardmwadsworth
Project: Animated Treasury Yeild Curve
"""
# Modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# Global variables
Today = dt.date.today()
File = 'TreasuryYields.csv'
Index_Error = 3
FieldNames = ['Date','1M','2M','3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y']
Web_http = 'http://data.treasury.gov/Feed.svc/DailyTreasuryYieldCurveRateData(7258)'
fmt  = '%Y-%m-%d'
TermList = ['NEW_DATE', 'BC_1MONTH','BC_2MONTH','BC_3MONTH','BC_6MONTH','BC_1YEAR',
            'BC_2YEAR','BC_3YEAR','BC_5YEAR','BC_7YEAR','BC_10YEAR','BC_20YEAR','BC_30YEAR']


# File handling routines...
# Save the Treasury yields you've just retrieved...
def Save_Treasury_Yield_Data( DF, file=File):
    # First, convert raw Treasury yield data to dataframe format
    # DF = pd.DataFrame( Yield_Data,columns=FieldNames, etc.)
    # Next, save in file...
    DF.to_csv(file,
              sep=' ',
              na_rep=np.nan,
              header=False,
              index=True,
              date_format=fmt)

# Obtain the Treasury yields from the saved file.
def Get_Treasury_DataFrame(file=File):
    DF = pd.read_csv( file,
                      sep=' ',
                      index_col=0, 
                      names=FieldNames[1:], 
                      parse_dates=True, 
                      infer_datetime_format=True)
    return DF.sort_index()


# TREASURY DEPT DATA SCRAPING
# To scrape yield data, it's necessary to use an index in the Web page address
# note that yield data goes back to 1990; the index
# was 1. For 01/02/19, the index is 7258. For 01/02/2018, 
# the index is 7009. This is the index we want to begin with.

def HTTP(Index=7258):
    return Web_http[:66] + str(Index) + ')'

# We can scrape off data from the Treasury Dept's yield page...
# Note: Treasury page indicates data in xml format
# Suggests that the best parser might be the lxml-xml

def Scrape(http, Parser='lxml-xml'):
    html_code = uReq(http)
    RawData = html_code.read()
    html_code.close()
    data = soup(RawData, Parser)
    return data

# The following function returns a list record of the date and
# the Treasury yields for that date
# Note that the Start_Index of 7258 refers to the first bond trading
# day of 2019

def Get_New_Daily_Yields(Start_Index=1, End_Index=10000):
    Dates = []
    List_of_Daily_Yields = []
    Index = Start_Index - 1
    while True:
        try:
            Index += 1
            if Index > End_Index:
                raise Exception
            Web_http = HTTP(Index)      # Get the next Web page http
            data = Scrape(Web_http)     # Retrieve data from Web page, and return a beautiful soup parsed object
            # Now, let's cumulate daily yields; note: missing data will preclude using list comprehension!
            Daily_Yields = []           
            for term in TermList:
                datum = data.find(term).contents
                if datum:
                    Daily_Yields.append(datum[0])
                else:
                    Daily_Yields.append(None)            # missing data precludes list comprehension
            Daily_Yields[0] = Daily_Yields[0][:10]       # reduce datetime to date only
            Dates.append(dt.datetime.strptime( Daily_Yields[0],fmt))
            List_of_Daily_Yields.append( Daily_Yields[1:])
        except:
            break
    # Convert List to DataFrame...    
    DF = pd.DataFrame( List_of_Daily_Yields, index=Dates, columns=FieldNames[1:], dtype=float).round(2)
    return DF.sort_index()


# This function appends new yield data to old
def Update_Yield_Data(Existing_DF, New_DF, SavetoFile=[]):
    DF = Existing_DF.append( New_DF)
    if SavetoFile:
        Save_Treasury_Yield_Data( DF, file=SavetoFile)
    return DF.sort_index()

def Animate_Yield_Curve( df, Rate=5):  # Rate is the no. frames per sec
    
    Mat = [0.0833, 0.1667, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
    Labels = ['Maturity (yrs)', 'Yield %', 'Evolution of Treasury Rates']
    
    Interval = int(round(1000/Rate,0))

    fig, ax = plt.subplots(figsize=[10,8])
    ax.grid(True)
    ax.set_xlabel(Labels[0])
    ax.set_ylabel(Labels[1])
    ax.set_title(Labels[2])
    ax.set_xlim(0, 35)
    ax.set_ylim(0, int( df.fillna(0).values.max()) + 1)
    line, = ax.plot(Mat, df.values[0], antialiased=False)
    
    def Yield_Curve( i):
        Legend = [str(df.index[i].date())]
        ax.legend(Legend)
        line.set_data(Mat,df.values[i])
        if df['2Y'].iloc[i] > df['10Y'].iloc[i]:
            line.set_color('r')
        else:
            line.set_color('g')
        return line,    
    
    ani = animation.FuncAnimation(fig, 
                                  Yield_Curve, 
                                  len(df), 
                                  interval=Interval,
                                  repeat=True
                                  ) 
    plt.show()

def YieldCurve(BeginDate='1990-01-02', Rate=20):
    Begin = dt.datetime.strptime( BeginDate,fmt)
    DF = Get_Treasury_DataFrame()
    Next_Index = len(DF) + Index_Error
    New_Data = Get_New_Daily_Yields(Next_Index) 
    DF = Update_Yield_Data(DF, New_Data, File)
    DF = DF[DF.index>=Begin]
    Animate_Yield_Curve(DF, Rate=Rate)
