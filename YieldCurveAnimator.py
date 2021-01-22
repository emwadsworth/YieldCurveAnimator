#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 00:59:26 2019
@author: edwardmwadsworth
Project: Animated Treasury Yeild Curve
"""

# Modules
import datetime as dt
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# Global constants
today = dt.date.today()
path = '/'
csvfile = 'treasury_yields.csv'
INDEX_ERROR = 3
FIELD_NAMES = ['Date', '1M', '2M', '3M', '6M', '1Y', '2Y', '3Y',
               '5Y', '7Y', '10Y', '20Y', '30Y']
T_HTTP = 'http://data.treasury.gov/Feed.svc/DailyTreasuryYieldCurveRateData(7258)'
fmt = '%Y-%m-%d'
TERM_LIST = ['NEW_DATE', 'BC_1MONTH', 'BC_2MONTH', 'BC_3MONTH', 'BC_6MONTH',
             'BC_1YEAR', 'BC_2YEAR', 'BC_3YEAR', 'BC_5YEAR', 'BC_7YEAR',
             'BC_10YEAR', 'BC_20YEAR', 'BC_30YEAR']


# File handling routines...
def save_treasury_yield_data(dataframe, file=path+csvfile):
    """
    Save the Treasury yields contained in the dataframe to a local file.
    """
    dataframe.to_csv(file,
                     sep=' ',
                     na_rep=np.nan,
                     header=False,
                     index=True,
                     date_format=fmt)


def get_treasury_dataframe(file=path+csvfile):
    """
    Obtain the Treasury yields from the saved file, and
    return as a dataframe sorted by index.
    """
    dataframe = pd.read_csv(file,
                            sep=' ',
                            index_col=0,
                            names=FIELD_NAMES[1:],
                            parse_dates=True,
                            infer_datetime_format=True)
    return dataframe.sort_index()


# TREASURY DEPT DATA SCRAPING
# To scrape yield data, it's necessary to use an index in the Web page address
# note that yield data goes back to 1990; the index
# was 1. For 01/02/19, the index is 7258. For 01/02/2018,
# the index is 7009. This is the index we want to begin with.
def next_http(Index=7258):
    """
    Return the URL of the web page to scrape.
    """
    return T_HTTP[:66] + str(Index) + ')'


# We can scrape off data from the Treasury Dept's yield page...
# Note: Treasury page indicates data in xml format
# Suggests that the best parser might be the lxml-xml
def scrape(http, parser='lxml-xml'):
    html_code = uReq(http)
    raw_data = html_code.read()
    html_code.close()
    data = soup(raw_data, parser)
    return data


# The following function returns a list record of the date and
# the Treasury yields for that date
# Note that a Start_Index of 7258 refers to the first bond trading
# day of 2019
# Index 6007 corresponds to 2014-01-01.
def get_new_daily_yields(start_index=6007, end_index=10000):
    dates = []
    list_of_daily_yields = []
    index = start_index - 1
    while True:
        try:
            index += 1
            if index > end_index:
                raise Exception
            web_http = next_http(index)      # Get the next Web page http
            data = scrape(web_http)  # Retrieve data from Web page,
            # &return a beautiful soup parsed object.
            # Cumulate daily yields;
            # note: missing data precludes use of list comprehension
            daily_yields = []
            for term in TERM_LIST:
                datum = data.find(term).contents
                if datum:
                    daily_yields.append(datum[0])
                else:
                    daily_yields.append(None)
            # reduce datetime to date only:
            daily_yields[0] = daily_yields[0][:10]
            dates.append(dt.datetime.strptime(daily_yields[0], fmt))
            list_of_daily_yields.append(daily_yields[1:])
        except:
            break
    # Convert List to DataFrame:
    dataframe = pd.DataFrame(list_of_daily_yields, index=dates,
                             columns=FIELD_NAMES[1:], dtype=float).round(2)
    return dataframe.sort_index()


# This function appends new yield data to old
def update_yield_data(existing_df, new_df, save_to_file=None):
    dataframe = existing_df.append(new_df)
    if save_to_file:
        save_treasury_yield_data(dataframe, file=save_to_file)
    return dataframe.sort_index()


def animate_yield_curve(dataframe, rate=5):  # Rate is the no. frames per sec
    maturities = [0.0833, 0.1667, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
    labels = ['Maturity (yrs)', 'Yield %', 'Evolution of Treasury Rates']
    interval = int(round(1000/rate, 0))
    fig, ax = plt.subplots(figsize=[10, 8])
    ax.grid(True)
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_title(labels[2])
    ax.set_xlim(0, 35)
    ax.set_ylim(0, int(dataframe.fillna(0).values.max()) + 1)
    line, = ax.plot(maturities, dataframe.values[0], antialiased=False)

    def yield_data(i):
        Legend = [str(dataframe.index[i].date())]
        ax.legend(Legend)
        line.set_data(maturities, dataframe.values[i])
        if dataframe['2Y'].iloc[i] > dataframe['10Y'].iloc[i]:
            line.set_color('r')
        else:
            line.set_color('g')
        return line,

    ani = animation.FuncAnimation(fig, 
                                  yield_data,
                                  frames=len(dataframe),
                                  interval=interval,
                                  repeat=True)
    plt.show()


def yield_curve(begin_date='1990-01-02', rate=5):
    begin = dt.datetime.strptime(begin_date, fmt)
    dataframe = get_treasury_dataframe()
    next_index = len(dataframe) + INDEX_ERROR
    new_data = get_new_daily_yields(next_index)
    dataframe = update_yield_data(dataframe, new_data, path+csvfile)
    dataframe = dataframe[dataframe.index >= begin]
    animate_yield_curve(dataframe, rate=rate)
