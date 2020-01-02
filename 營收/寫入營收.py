# -*- coding: utf-8 -*-

import os
from datetime import datetime
import pandas as pd

import re
import numpy as np
from sqlalchemy import create_engine
import mysql.connector
import csv
import time
import shutil
import os
import io
from pandas import isnull
from glob import glob

ip = '127.0.0.1'

enginePi = create_engine( 'mysql+mysqlconnector://pregaine:RF69xy7C@{}/mysql?charset=utf8'.format( ip ) )

class DB_Revenue:
    def __init__( self, server, database, username, password ):

        self.df = pd.DataFrame( )
        self.src_df = pd.DataFrame( )

        self.datelst = [ ]
        print( "Initial Database connection..." + database )
        self.dbname = database
        
        self.con_db = mysql.connector.connect( host     = server,
                                               user     = username,
                                               passwd   = password,
                                               database = database,
                                               charset  = "utf8"
                                              )

        self.cur_db = self.con_db.cursor( buffered = True )
        self.con_db.commit( )

    def Reset_Table( self ):
    
        self.cur_db.execute( '''DROP TABLE IF EXISTS REVENUE;''' )
        
        print( 'Successfuly Deleter REVENUE Table' )

    def CreatDB( self ):

        cmd = '''

            CREATE TABLE mysql.REVENUE
        	(
                stock varchar( 10 ) COLLATE utf8_bin NOT NULL,
                date date NOT NULL,
                
                Month_Revenue decimal( 16, 0 ) NULL,
                Last_Month_Revenue decimal( 16, 0 ) NULL,
                Last_Year_Revenue decimal( 16, 0 ) NULL,
                
                Last_Month_Ratio float NULL,
                Last_Year_Ration float NULL,
                
                Month_Acc_Revenue decimal( 16, 0 ) NULL,
                Last_Year_Acc_Revenue decimal( 16, 0 ) NULL,
                
                ration float NULL

        	)'''

        self.cur_db.execute( cmd )

        print( 'Successfuly Create 營收' )

    def GetDateLst( self, value ):

        datelst = [ ]

        stock_id = self.GetStockID( value )

        ft = self.cur_db.execute( 'SELECT date_id FROM MarginTrad WHERE stock_id = (?)', (stock_id,) ).fetchall( )

        if ft is not None:
            for val in ft:
                value = self.cur_db.execute( 'SELECT date FROM Dates WHERE id = ( ? )', (val) ).fetchone( )[ 0 ]
                datelst.append( value.strftime( '%Y%m%d' ) )

        return datelst

    def CompareDB( self, year, month ):

        cmd = 'SELECT stock, Month_Revenue FROM REVENUE WHERE MONTH( date ) = \'{0}\' AND YEAR( date ) = \'{1}\''.format( month, year )
        
        ft = self.cur_db.execute( cmd )
        
        ft = self.cur_db.fetchall( )

        lst = [ ]

        for val in ft:
            stock = val[ 0 ]
            Month_Revenue = val[ 1 ]
            lst.append( ( stock, Month_Revenue ) )

        df_db = pd.DataFrame( lst, columns = [ '公司代號', 'Month_Revenue_FromDB' ] )
        left = pd.merge( self.df, df_db, on = [ '公司代號' ], how = 'left' )

        left = left[ left[ 'Month_Revenue_FromDB' ] != left[ '當月營收' ] ]
        del left[ 'Month_Revenue_FromDB' ]
        self.df = left

        # print( self.df )

    def GetStockDF( self, value ):

        datelst = [ ]

        stock_id = self.GetStockID( value )

        ft = self.cur_db.execute( 'SELECT date_id FROM Tdcc WHERE stock_id = (?)', (stock_id,) ).fetchall( )

        if ft is not None:
            for val in ft:
                value = self.cur_db.execute( 'SELECT date FROM Dates WHERE id = ( ? )', (val) ).fetchone( )[ 0 ]
                datelst.append( value.strftime( '%Y%m%d' ) )

        return datelst

    def ReadCSV( self, file ):

        self.df = pd.read_csv( file, sep = ',', encoding = 'utf8', false_values = 'NA', dtype = { '公司代號': str } )

        del self.df[ '產業別' ]
        del self.df[ '公司名稱' ]

        # self.df[ '日期' ] = pd.to_datetime( self.df[ '日期' ], format = "%y%m%d" )
        # print( self.df )

    def WriteDB( self, year, month ):

        self.df = self.df.astype( object ).where( pd.notnull( self.df ), None )

        if self.df.empty:
            # print( '{:<7}exist DB'.format( self.stock ) )
            return

        lst = self.df.values.tolist( )

        for val in lst:

            val = [ None if i == u'不適用' else i for i in val ]
            val.pop( 0 )
            val.insert( 1, '{0}-{1}-15'.format( year, month ) )

            var_string = ', '.join( ['%s'] * ( len( val )  ) )
            query_string = 'INSERT INTO mysql.REVENUE VALUES ( {} );'.format( var_string )

            self.cur_db.execute( query_string, val )

            # print( query_string, val )

            print( '寫入資料庫 {} {}'.format( val[ 0 ], val[ 1 ] ) )



def main( ):

    db = DB_Revenue( ip, 'mysql', 'pregaine', 'RF69xy7C' )
  
    db.Reset_Table( )
    db.CreatDB( )

    # 讀取資料夾
    for file in os.listdir( './' ):

        if file.endswith( ".csv" ) != 1:
            continue

        year  = file[ 5:9 ]
        month = file[ 9:11 ]
        # print( "year {} month {} file {}".format( year, month, file ) )

        db.ReadCSV( file )
        db.CompareDB( year, month )
        db.WriteDB( year, month )
        db.con_db.commit( )

if __name__ == '__main__':

    start_tmr = datetime.now( )
    main( )
    print( datetime.now( ) - start_tmr )