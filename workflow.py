#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import re
import calendar
import datetime

# @begin DataWrangling_Farmers.csv @desc Data Cleaning
# @param farmers.csv
def form_address(rows):
        """
        Form address will return the address using the columns
        listed below, if any of the columns is not available
        it will return an empty string.
        """
        cols = ['street', 'city', 'State', 'zip']
        if any([not rows[c] for c in cols]):
            return ''
        else:
            return ', '.join([rows[c] for c in cols])

def is_valid_url(url):
    """
    Takes any string and returns it if it's a valid url
    returns and empty string otherwise.
    """
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if regex.search(url):
        return url
    else:
        return ''

#ensure twitter uses @
def format_twitter(row):
    if 'https://twitter.com/' in row:
        return row.replace('https://twitter.com/', '@')
    elif row and '@' not in row:
        return '@' + row
    elif '@' in row:
        return row
    else:
        return ''

def is_valid_season(row):
    """
    Returns the row if the season in the format
    "%m/%d/%Y" to "%m/%d/%Y", otherwise it sends the
    row to another function for further inspecting.
    """
    pattern = re.compile("\d+/\d+/\d+ to \d+/\d+/\d+")
    if pattern.match(row.strip()):
        return row
    else:
        return get_valid_season(row)

def get_valid_season(row):
    """
    This is the second step for season dates inspection,
    if the season is formatted with names of months it will use
    the current year for the season, otherwise it will send an
    empty string back.
    """
    vals = row.strip().split(" to ")
    months = {v: k for k,v in enumerate(calendar.month_name)}
    del months[''] #empty not a valid month
    if not vals:
        return ''
    elif not all([val in list(months.keys()) for val in vals]):
        return ''
    elif len(vals) > 2: #we are only expecting two
        return ''
    else:
        year = datetime.datetime.now().year
        dt1 = datetime.datetime(year=year, month=months[vals[0]], day=1)
        dt2 = datetime.datetime(year=year, month=months[vals[1]], day=1)
        return dt1.strftime("%m/%d/%Y") + " to " + dt2.strftime("%m/%d/%Y")

if __name__ == '__main__':
    # @begin read_csv
    # @in farmers.csv
    df = pd.read_csv('farmers.csv')
    # @out DataFrame @desc Collect data set using the given data collection parameters.
    # @end read_csv
    # @begin Clean_UpdateTime
    # @in DataFrame @desc unformatted time
    df['updateTime'] = pd.to_datetime(df['updateTime']) #does the heavy lifting
    df['updateTime'] = df['updateTime'].apply(lambda x: x.strftime("%Y-%m-%d"))
    # @out updateTime
    # @end Update_Time
    # --------------------------------------------------------------------------
    # @begin Replace_Nans
    # @in DataFrame
    df = df.replace(np.nan, '', regex=True)
    # @out EmptyStrings
    # @end Replace_Nans
    # --------------------------------------------------------------------------
    # @begin Form_Address
    # @in DataFrame
    address = df.apply(form_address, axis=1)
    idx = df.columns.get_loc('zip') + 1
    df.insert(idx, 'FullAddress', address)
    # @out FullAddress
    # @end Form_Address
    # --------------------------------------------------------------------------
    # @begin InputeBinCols
    # @in DataFrame
    bin_cols = df.iloc[:,23:-1].columns
    for col in bin_cols:
        mask = mask = np.argwhere(df[col] != 'Y').ravel().tolist()
        df.loc[mask, col] = "N"
    # @out BinCols
    # @end InputeBinCols
    # --------------------------------------------------------------------------
    # @begin Validate_SocialMedia
    # @in DataFrame
    df['Facebook'] = df['Facebook'].apply(is_valid_url)
    df['Website'] = df['Website'].apply(is_valid_url)
    df['Youtube'] = df['Youtube'].apply(is_valid_url)
    df['Twitter'] = df['Twitter'].apply(format_twitter)
    # @out ValidSocialInfo
    # @end Validate_SocialMedia
    # --------------------------------------------------------------------------
    # @begin Drop_Geo_Locators
    # @in DataFrame
    df = df.drop(columns=['x','y'])
    # @end Drop_Geo_Locators
    # --------------------------------------------------------------------------
    # @begin FormatSeasonInfo
    # @in DataFrame
    df['Season1Date'] = df['Season1Date'].apply(is_valid_season)
    df['Season2Date'] = df['Season2Date'].apply(is_valid_season)
    df['Season3Date'] = df['Season3Date'].apply(is_valid_season)
    df['Season4Date'] = df['Season4Date'].apply(is_valid_season)
    # @out ValidSeasonInfo
    # @end FormatSeasonInfo
    # --------------------------------------------------------------------------
    # @begin DataFrame
    # @in ValidSeasonInfo
    # @in ValidSocialInfo
    # @in BinCols
    # @in FullAddress
    # @in EmptyStrings
    # @in updateTime
    # @out CleanDataFrame
    # @end DataFrame
    # --------------------------------------------------------------------------
    # @begin CleanFarmers.csv
    # @in CleanDataFrame
    df.to_csv('CleanFarmers.csv', index=False)
    # @end CleanFarmers.csv


# @end DataWrangling_Farmers.csv
