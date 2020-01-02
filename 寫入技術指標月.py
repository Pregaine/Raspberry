#coding=utf-8
#!/home/pi/miniconda3/envs/py36/bin/python

from datetime import datetime
import pandas as pd
import re
import numpy as np
from sqlalchemy import create_engine
import mysql.connector
import re
import csv
import time
import shutil
import os
import io
from pandas import isnull
from glob import glob

# ip = '182.155.205.224'

ip = '127.0.0.1'

# engine = create_engine( "mysql+mysqldb://root:28wC75#D@127.0.0.1/StockDB?charset=utf8" )

enginePi = create_engine( 'mysql+mysqlconnector://pregaine:RF69xy7C@{}/mysql?charset=utf8'.format( ip ) )

def StrToDateFormat( data, val ):
    # print( 'data {}, val {}'.format( data, val ) )
    
    dt = datetime.strptime( val, '%y%m%d' )
    val = dt.strftime( "%y-%m-%d" )

    return val


class DB_TechAnalysis:

    def __init__( self, server, database, username, password ):

        self.df = pd.DataFrame( )
        self.src_df = pd.DataFrame( )

        self.d = { '月': 'TECH_M' }

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

        #  TODO 如何查當下SQL 語言及時間格式
        # cmd = """SET LANGUAGE us_english; set dateformat ymd;"""
        # self.cur_db.execute( cmd )

        self.stock = ''
        self.date = ''

    def ResetTable( self, data ):

        d = dict( 分 = 'DROP TABLE IF EXISTS TECH_H', 
                  日 = 'DROP TABLE IF EXISTS TECH_D',
                  周 = 'DROP TABLE IF EXISTS TECH_W', 
                  月 = 'DROP TABLE IF EXISTS TECH_M' )

        # Do some setup
        self.cur_db.execute( d[ data ] )
            
        print( 'Successfully Deleter ' + data )

    def CreateTable( self, data ):

          
        sql_m_cmd = '''
        CREATE TABLE mysql.TECH_M 
        (
        stock varchar( 10 ) COLLATE utf8_bin NOT NULL,
        date DATE NOT NULL,
        
        open_price decimal(10, 2) NULL,
        high_price decimal(10, 2) NULL,
        low_price decimal(10, 2) NULL,
        close_price decimal(10, 2) NULL,
        volume bigint NULL,
        
        ma3 decimal(10, 2) NULL,
        ma6 decimal(10, 2) NULL,
        ma12 decimal(10, 2) NULL,
        ma24 decimal(10, 2) NULL,
        ma36 decimal(10, 2) NULL,
        ma60 decimal(10, 2) NULL,
        ma120 decimal(10, 2) NULL,
        
        rsi2 decimal(10, 2) NULL,
        rsi5 decimal(10, 2) NULL,
        rsi10 decimal(10, 2) NULL,
        
        k9_3 decimal(10, 2) NULL,
        d9_3 decimal(10, 2) NULL,
        k3_2 decimal(10, 2) NULL,
        d3_3 decimal(10, 2) NULL,
        
        mfi4 decimal(10, 2) NULL,
        mfi6 decimal(10, 2) NULL,
        mfi14 decimal(10, 2) NULL,

        macd_dif_6 decimal(10, 2) NULL,
        dem_12 decimal(10, 2) NULL,
        osc_6_12_9 decimal(10, 2) NULL,

        macd_dif_12 decimal(10, 2) NULL,
        dem_26 decimal(10, 2) NULL,
        osc6_12_26_9 decimal(10, 2) NULL,

        willr9 decimal(10, 2) NULL,
        willr18 decimal(10, 2) NULL,
        willr42 decimal(10, 2) NULL,
        willr14 decimal(10, 2) NULL,
        willr24 decimal(10, 2) NULL,
        willr56 decimal(10, 2) NULL,
        willr72 decimal(10, 2) NULL,
        
        plus_di decimal(10, 2) NULL,
        minus_di decimal(10, 2) NULL,
        dx decimal(10, 2) NULL,
        adx decimal(10, 2) NULL,
        upperband decimal(10, 2) NULL,
        middleband decimal(10, 2) NULL,
        dnperband decimal(10, 2) NULL,
        bb decimal(10, 2) NULL,
        w20 decimal(10, 2) NULL,
        bias20 decimal(10, 2) NULL,
        bias60 decimal(10, 2) NULL,

        INDEX name ( stock, date ),
        INDEX idx_stock ( stock ),
        INDEX idx_date ( date )

        )
        '''

        table_d = { '月': sql_m_cmd }

        self.cur_db.execute( table_d[ data ] )
        
        print( 'Successfully Create 技術指標 ' + data )

    def CompareDB( self, data ):
    
        # print( table_name, stock_num )
        
        cmd = 'SELECT date, volume FROM {0} WHERE stock = \'{1}\''.format( self.d[ data ], self.stock )
        
        self.cur_db.execute( cmd )
        
        ft = self.cur_db.fetchall( )
 
        lst = [ ]

        for val in ft:
            
            date = val[ 0 ].strftime( '%y%m%d' )

            volume = val[ 1 ]
            
            lst.append( ( date, volume ) )

        df = pd.DataFrame( lst, columns = [ '日期', '成交量_資料庫取出' ] )
        # print( df.head( 5 ) )
        left = pd.merge( self.df, df, on = [ '日期' ], how = 'left' )
        left = left[ left[ '成交量_資料庫取出' ] != left[ '成交量' ] ]
        del left[ '成交量_資料庫取出' ]
        
        self.df = left  
        
        for index, row in self.df.iterrows( ):
            # print( self.stock, row[ '日期' ] )
            self.FindDuplicate( row[ '日期' ] )
        
        # print( data, '刪除重覆寫入' )
        # print(  self.df )

    def ReadCSV( self, file ):
    
        self.df = pd.read_csv( file, 
                               sep = ',', 
                               encoding = 'utf8', 
                               false_values = 'NA', 
                               dtype = { '日期': str } )
                               
        self.df = self.df.replace( [ np.inf, -np.inf ], np.nan )  
        
        # self.df = self.df[ : 20 ]
        # self.df[ '日期' ] = pd.to_datetime( self.df[ '日期' ], format = "%y%m%d" )  
        # print( self.df )

    def FindDuplicate( self, data ):

        # 尋找重覆資料
        cmd = 'SELECT stock, date from mysql.TECH_M where stock = \'{}\' and date = \'{}\';'.format( self.stock, data )
        
        # print( cmd )
        
        self.cur_db.execute( cmd )
        
        ft = self.cur_db.fetchone( )
        
        # print( '比對資料庫{0:>10} {1}'.format( self.stock, data ) )

        if ft is not None:
        
            cmd = '''DELETE FROM mysql.TECH_M where stock = \'{}\' and date = \'{}\';'''.format( self.stock, data )
            
            # print( cmd )
            
            self.cur_db.execute( cmd )
            
            print( '刪除重覆資料{0:>10} {1}'.format( self.stock, data ) )
            
            self.con_db.commit( )

        '''
        # 尋找重覆資料
        # cmd = 'SELECT stock, date from mysql.TECH_W WHERE stock = \'{}\' and date = \'{}\';'.format( self.stock, data )
        
        # print( cmd )
        
        self.cur_db.execute( cmd )
        
        ft = self.cur_db.fetchone( )
        
        # print( '比對資料庫{0:>10} {1}'.format( self.stock, data ) )

        if ft is not None:
        
            cmd = 'DELETE FROM mysql.TECH_W WHERE stock = \'{}\' and date = \'{}\';'.format( self.stock, data )
            
            # print( cmd )
            
            self.cur_db.execute( cmd )
            
            print( '刪除重覆資料{0:>10} {1}'.format( self.stock, data ) )
            
            self.con_db.commit( )
        '''

    def WriteDB( self, data ):
    
        
        '''
        self.df = self.df.astype( object ).where( pd.notnull( self.df ), None )

        lst = self.df.values.tolist( )

        if len( lst ) == 0:
            # print( '資料庫比對CSV無新資料 {}'.format( self.stock ) )
            return
                    
        columns = [ 'stock', 'date', 'open_price', 'high_price ', 'low_price', 'close_price', 'volume',
                    'ma4', 'ma12', 'ma24', 'ma48', 'ma96', 'ma144', 'ma240', 'ma480', 'rsi2', 'rsi3',
                    'rsi4', 'rsi5', 'rsi10', 'k9_3', 'd9_3', 'k3_2', 'd3_3', 'mfi4', 'mfi6', 'mfi14',
                    'macd_dif_6', 'dem_12', 'osc_6_12_9', 'macd_dif_12', 'dem_26', 'osc6_12_26_9', 'willr9',
                    'willr18', 'willr42', 'willr14', 'willr24', 'willr56', 'willr72', 'plus_di', 'minus_di',
                    'dx', 'adx', 'upperband', 'middleband', 'dnperband', 'bb', 'w20', 'bias20', 'bias60' ]
        
        lenVal = len( columns )
        
        var_string = ','.join( [ '%s' ] * lenVal )
        
        for val in lst:
                                            
            val[ 0 ] = self.stock
            
            # print( val )            
            # exit()
            
            # dt = datetime.strptime( val[ 1 ], '%y%m%d' )
            # val[ 1 ] = dt.strftime( "%y-%m-%d" )
                      
            query_string = 'INSERT INTO mysql.TECH_W VALUES ( {} );'.format( var_string )

            # print( query_string )
            # print( '取出{}'.format( val ) )
           
            self.cur_db.execute( query_string, val )
            
            print( '寫入資料庫 {} {}'.format( val[ 0 ], val[ 1 ] ) )
            
        '''    
                
        
        self.df = self.df.astype( object ).where( pd.notnull( self.df ), None )

        if self.df.empty:
            # print( '{:<7}exist DB'.format( self.stock ) )
            return

        del self.df[ 'Unnamed: 0' ]
        self.df.insert( 0, 'stock', self.stock )

        # self.df[ '日期' ] = pd.to_datetime( self.df[ '日期' ], format = '%y%m%d' )
        # self.df[ '日期' ] = self.df[ '日期' ].dt.strftime( "%y-%m-%d" )

        # print( self.df, self.d[ data ] )

    
        self.df.columns = [ 'stock', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume',
                            'ma3', 'ma6', 'ma12', 'ma24', 'ma36', 'ma60', 'ma120',
                            'rsi2', 'rsi5', 'rsi10', 
                            'k9_3', 'd9_3', 'k3_2', 'd3_3', 
                            'mfi4', 'mfi6', 'mfi14',
                            'macd_dif_6', 'dem_12', 'osc_6_12_9', 'macd_dif_12', 'dem_26', 'osc6_12_26_9', 
                            'willr9', 'willr18', 'willr42', 'willr14', 'willr24', 'willr56', 'willr72',
                            'plus_di', 'minus_di',
                            'dx', 'adx', 'upperband', 'middleband', 'dnperband', 'bb', 'w20', 'bias20', 'bias60' ]


        # Try to send it to the access database (and fail)
        self.df.to_sql( name = self.d[ data ], 
                        con = enginePi, 
                        index = False, 
                        if_exists = 'append', 
                        index_label = None )
                        
        print( '寫入資料庫{0:>2}{1:>7} {2}'.format( data, self.stock, self.date ) )

def main( ):
    
    db_M = DB_TechAnalysis( ip, 'mysql', 'pregaine', 'RF69xy7C' )
    
    #  移除表格
    db_M.ResetTable( '月' )

    #  建立資料表
    db_M.CreateTable( '月' )
    
    stock_M = { '月': [ db_M, '_月線技術指標.csv' ] }

    path = '/home/pi/Downloads/技術指標/month/'

    # 讀取資料夾
    for file in glob( '{}*_月線技術指標.csv'.format( path ) ):
                              
        if os.path.getsize( file ) == 0:
            continue
            
        num = file.split( '_' )[ 0 ]
        num = num.replace( path, '' )
        data = file[ -10:-9 ]

        # print( file )

        if data in stock_M.keys( ):
        
            Obj = stock_M[ data ][ 0 ]
            Obj.stock = num
            
            print( '讀取 {}'.format( file ) )
            print( '股號 {}'.format( num ) )
            
            print( data )
     
            # if num != '2887':
                # continue

            Obj.ReadCSV( file )
            Obj.CompareDB( data )           
            Obj.WriteDB( data )

        else:
            print( '讀取錯誤 {}'.format( data ) )
            
        # exit()
    
if __name__ == '__main__':

    start_tmr = time.time( )
    main( )
    print( '{:04.1f}'.format( (time.time( ) - start_tmr) ) )
