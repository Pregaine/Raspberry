# -*- coding=utf-8 -*-
import sys
import requests
import numpy as np
import pandas as pd
import talib
from datetime import datetime, timedelta
import threading
import math
import time
from bs4 import BeautifulSoup as BS
import os
# import codes.codes as TWSE
from sqlalchemy import create_engine
import mysql.connector

engine = create_engine( "mysql+mysqlconnector://pregaine:RF69xy7C@127.0.0.1/mysql?charset=utf8" )

# stock_lst = list( TWSE.codes.keys( ) )

stock_lst = [ '2317' ]

stock_list_path = r'/home/pi/Downloads/StockList_股本.csv'

df = pd.read_csv(
    stock_list_path,
    lineterminator='\n',
    encoding='utf8',
    sep=',',
    index_col=False,
    na_filter=False,
    thousands=',')

df['代號'] = df['代號'].str.strip('="')
df['stock'] = df['代號'].astype(str)
del df['代號']

# df['股本(億)'] = df['股本(億)\r']
# del df['股本(億)\r']

df.sort_values(by=['股本(億)'], ascending=False, inplace=True)
df.reset_index(inplace=True)

del df['index']
df = df[ df['股本(億)'] > 10 ]


# tmp_df = pd.DataFrame( columns = df.columns )

tmp_df = pd.DataFrame( columns = [ '股名', '股號', '觀察日', '買進日', '買進價', '賣出日', '賣出價', '損益' ] )

SelectCmd = """
            SELECT
            stock
            FROM mysql.TECH_W WHERE
            date > '2019-06-01' AND
            volume > 2000 AND
            k3_2 < 15 AND
            rsi2 < 15 AND
            mfi4 < 5 AND
            close_price > 10
            GROUP BY stock;"""

tech_w_cmd = """SELECT
                stock,
                date,
                open_price,
                close_price,
                high_price,
                low_price,
                volume,
                k3_2,
                rsi2,
                mfi4
                FROM mysql.TECH_W WHERE stock = \'{}\' AND date > '2019-06-01' ORDER BY date DESC"""

# df = df[ df['stock'] == '1262' ]
SelectDf = pd.read_sql_query( SelectCmd, engine )

# print ( '{ "id": 1, "name": "A green", "price": 12.50, "tags": [ "home", "green" ] }' )


# print( SelectDf.shape )

for queryNum in SelectDf[ 'stock' ]:

    stockNum = queryNum.decode( 'utf8' )
    
    Df = pd.read_sql_query( tech_w_cmd.format( stockNum ), engine )
    Df = Df.dropna()
    
    # exit()
    # print( '總列', len( Df.index ) )
    
    if len( Df.index ) < 11: 
        continue

    val = len( Df.index ) - 5
    pre_num  = None
    pre_date = None
        
    for pre_day in range( val, -1, -1 ):
        
        flag = 0
        w_this = pre_day
        w_last = pre_day + 1
             
        if pre_day > 0:
            w_next = pre_day - 1
        else:
            w_next = 0
            
        # print( 'next', w_next )    
        # print( 'this', w_this )
        # print( 'last', w_last )
        
        if Df.loc[ w_this, 'close_price' ] < 10:
            continue

        if Df.loc[ w_this, 'mfi4' ] < 5 or Df.loc[ w_last, 'mfi4' ] < 5 or Df.loc[ w_last + 1, 'mfi4' ] < 5 or Df.loc[ w_last + 2, 'mfi4' ] < 5:
            flag = flag + 1
            
        
        if Df.loc[ w_this, 'rsi2' ] < 15: 
            flag = flag + 1
            
        if Df.loc[ w_this, 'k3_2' ] < 15:
            flag = flag + 1
            
        '''
        if Df.loc[ w_this, 'k3_2' ] > Df.loc[ w_last, 'k3_2' ]:
            if Df.loc[ w_last, 'k3_2' ] < 15:
                flag = flag + 1
        
        
        if Df.loc[ w_this, 'rsi2' ] > Df.loc[ w_last, 'rsi2' ]:
            if Df.loc[ w_last, 'rsi2' ] < 15:
                flag = flag + 1
        '''

        if flag < 3:
            continue
            
        try:
            date = Df.loc[ pre_day, 'date' ]
            name = df.loc[ df[ 'stock' ] == stockNum, '名稱' ].values[ 0 ]
        except:
            continue
            
        # val_ = df.loc[ df[ 'stock' ] == query_num, '股本(億)' ].values[ 0 ]

        if pre_num == stockNum and pre_date == date:
            continue

        tmp_df = tmp_df.append( { '股號': stockNum, '股名': name, '觀察日':date }, ignore_index=True )

        condition = ( tmp_df.loc[ ( tmp_df['股號'] == stockNum ) & ( tmp_df['觀察日'] == date ) ].index )
    
        buy_price = ( Df.loc[ w_next, 'high_price' ] + Df.loc[ w_next, 'low_price' ] ) / 2
        buy_date = Df.loc[ w_next, 'date' ]

        weekCnt = 0

        for weekVal in range( w_next, - 1, -1 ):

            sell_price = ( Df.loc[ weekVal, 'high_price' ] +  Df.loc[ weekVal, 'low_price' ] ) / 2

            if ( ( sell_price - buy_price ) / buy_price ) > 0.03:
                break

            weekCnt += 1
            if weekCnt > 5:
                break

        # print( tech_w_df[ 0:3 ] )
        # tmp_df.loc[ condition, '符合' ]   = flag
        tmp_df.loc[ condition, '買進日' ] = Df.loc[ w_next, 'date' ]
        tmp_df.loc[ condition, '買進價' ] = buy_price
        tmp_df.loc[ condition, '賣出日' ] = Df.loc[ weekVal, 'date' ]
        tmp_df.loc[ condition, '賣出價' ] = sell_price
        tmp_df.loc[ condition, '損益' ]   = round( ( sell_price - buy_price ) / buy_price * 100, 1 )
        
        pre_num = stockNum
        pre_date = date
                       
        # print( tmp_df )
        # exit()
         
# tmp_df.sort_values( [ '損益' ], inplace=True, ascending=[ False ] )
# tmp_df = tmp_df.reset_index( )
# del tmp_df[ 'index' ]

# print( tmp_df )
tmp_df[ '買進日' ] = pd.to_datetime( tmp_df[ '買進日' ], format='%Y-%m-%d' )
tmp_df[ '賣出日' ] = pd.to_datetime( tmp_df[ '賣出日' ], format='%Y-%m-%d' )
tmp_df[ '觀察日' ] = pd.to_datetime( tmp_df[ '觀察日' ], format='%Y-%m-%d' )

tmp_df[ '買進日' ] = tmp_df[ '買進日' ].dt.strftime( '%Y-%m-%d' )
tmp_df[ '賣出日' ] = tmp_df[ '賣出日' ].dt.strftime( '%Y-%m-%d' )
tmp_df[ '觀察日' ] = tmp_df[ '觀察日' ].dt.strftime( '%Y-%m-%d' )

# print( tmp_df[ : 3 ].to_json( force_ascii = False, index = False, orient='table'  ) )

print( tmp_df.to_json( force_ascii = False, orient='index' ) )

# tmp_df.style

# returnStr = '{ "id": 1, "name": "A green", "price": 12.50, "tags": [ "home", "green" ] }'

# print( returnStr )