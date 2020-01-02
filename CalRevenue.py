# -*- coding=utf-8 -*-
# import requests
# import numpy as np
# import talib
# from datetime import datetime, timedelta
# import math
# import time
# from bs4 import BeautifulSoup as BS
# import os
# import warnings
# import mysql.connector

import sys
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine( "mysql+mysqlconnector://pregaine:RF69xy7C@127.0.0.1/mysql?charset=utf8" )

query_num = sys.argv[ 1 ]

# cmd = """SELECT
#         date,
#         Month_Revenue,
#         Last_Month_Revenue,
#         Last_Year_Revenue,
#         Last_Month_Ratio,
#         Last_Year_Ration,
#         Month_Acc_Revenue,
#         Last_Year_Acc_Revenue,
#         ration
#         FROM mysql.REVENUE WHERE stock = \'{}\' ORDER BY date DESC"""

cmd = """SELECT
        date,
        Month_Revenue
        FROM mysql.REVENUE WHERE stock = \'{}\' ORDER BY date DESC LIMIT 100"""

revenue_df = pd.read_sql_query( cmd.format( query_num ), engine )

revenue_df[ 'date' ] = pd.to_datetime( revenue_df[ 'date' ], format='%Y-%m-%d' )

revenue_df[ 'history_revenue_01' ] = revenue_df[ 'Month_Revenue' ].shift( 12*1 )
revenue_df[ 'history_revenue_01' ] = revenue_df[ 'history_revenue_01' ].shift( -12*2 )
# revenue_df[ 'history_revenue_01%' ] = ( revenue_df[ 'Month_Revenue' ] - revenue_df[ 'history_revenue_01' ] ) / revenue_df[ 'history_revenue_01' ] * 100
# -------------------------

revenue_df[ 'history_revenue_03' ] = revenue_df[ 'Month_Revenue' ].shift( 12*1 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*2 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*3 )

revenue_df[ 'history_revenue_03' ] = revenue_df[ 'history_revenue_03' ].shift( -12*4 )
revenue_df[ 'history_revenue_03' ] = revenue_df[ 'history_revenue_03' ] / 3
# revenue_df[ 'history_revenue_03%' ] = ( revenue_df[ 'Month_Revenue' ] - revenue_df[ 'history_revenue_03' ] ) / revenue_df[ 'history_revenue_03' ] * 100 
# -------------------------

revenue_df[ 'history_revenue_05' ] = revenue_df[ 'Month_Revenue' ].shift( 12*1 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*2 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*3 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*4 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*5 )

revenue_df[ 'history_revenue_05' ] = revenue_df[ 'history_revenue_05' ].shift( -12*6 )
revenue_df[ 'history_revenue_05' ] = revenue_df[ 'history_revenue_05' ] / 5 
# revenue_df[ 'history_revenue_05%' ] = ( revenue_df[ 'Month_Revenue' ] - revenue_df[ 'history_revenue_05' ] ) / revenue_df[ 'history_revenue_05' ] * 100
# -------------------------

revenue_df[ 'history_revenue_08' ] = revenue_df[ 'Month_Revenue' ].shift( 12*1 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*2 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*3 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*4 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*5 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*6 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*7 ) + \
                                     revenue_df[ 'Month_Revenue' ].shift( 12*8 )      
                            
revenue_df[ 'history_revenue_08' ] = revenue_df[ 'history_revenue_08' ].shift( -12*9 )
revenue_df[ 'history_revenue_08' ] = revenue_df[ 'history_revenue_08' ] / 8 

# revenue_df[ 'history_revenue_08%' ] = ( revenue_df[ 'Month_Revenue' ] - revenue_df[ 'history_revenue_08' ] ) / revenue_df[ 'history_revenue_08' ] * 100

# revenue_df[ [ 'date', 'history_revenue_03%', 'history_revenue_05%', 'history_revenue_08%' ] ].head( 48 )
# -------------------------

# warnings.filterwarnings( "ignore", category=RuntimeWarning )

revenue_df = revenue_df.round(0)

# 輸出排序欄位 
# 日期,
# 當月營收,
# 去年同期當月營收平均,
# 前3年同期月營收平均,
# 前5年同期月營收平均
# 前8年同期月營收平均

print( revenue_df.to_json( force_ascii = False, orient='values' ) )
