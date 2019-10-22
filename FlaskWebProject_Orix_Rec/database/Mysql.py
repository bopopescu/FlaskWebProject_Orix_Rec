# database
#from sqlalchemy import create_engine
import pymysql.cursors
import mysql.connector
import sqlite3

from tqdm import tqdm

# multi
from multiprocessing import Pool
from joblib import Parallel, delayed
from time import time
from concurrent.futures import ProcessPoolExecutor

class Mysql:
    def __init__(self, host='172.31.19.191', db_name='orix_data', user='root'):
        self.con = mysql.connector.connect(
        host=host,
        db=db_name,
        user=user,
        passwd='0gur11a6'
        )
        self.cur = self.con.cursor(dictionary=True)
        self.sql_out = []


    def sql_excute_fetch(self, sql):
        ##print(sql)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        #self.sql_out = rows
        #print(self.sql_out)
        #return self.sql_out
        return rows

    def limit_calc_avg(self, num):

        # データベース接続
        con = mysql.connector.connect(
        host='172.31.19.191',
        db='orix_data',
        user='root',
        passwd='0gur11a6'
        )
        cur = con.cursor(dictionary=True)

        rows = mysql.sql_excute_fetch('SELECT * FROM `limit_velocity` WHERE  id = ' + str(num))
        sql_avg_v = 'SELECT  AVG(velocity_kmh) FROM `Drive_recorder` WHERE ' + str(rows[0]['longitude']) + ' = CAST(`longitude`*1000 AS INT)/1000  AND ' + str(rows[0]['latitude']) + '=  CAST(`latitude`*1000 AS INT)/1000 AND velocity_kmh > 20'
        rows_avg_v =  mysql.sql_excute_fetch(sql_avg_v)

        sql = "UPDATE `limit_velocity` SET velocity_avg=" + str(rows_avg_v[0]['AVG(velocity_kmh)']) + " WHERE id=" + str(num)
        #self.cur.execute(sql)
        #self.con.commit()
        self.cur.execute(sql)
        self.con.commit()
        print()
        return rows_avg_v


if __name__ == '__main__':
    mysql = Mysql(host='172.31.19.191', db_name='orix_data', user='root')
    #sql_out = mysql.sql_excute_fetch('SELECT * FROM `limit_velocity` WHERE sub = 1')

    id_list = list(range(1, 33792))

    with ProcessPoolExecutor() as executor:
        for rows_avg_v in executor.map(mysql.limit_calc_avg, id_list):
            print(rows_avg_v)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    pool = Pool(processes=30)
    with tqdm(total=len(id_list)) as t:
        for _ in pool.imap_unordered(mysql.limit_calc_avg, id_list):
            t.update(1)

    """

    r = Parallel(n_jobs=30)( [delayed(mysql.limit_calc_avg)(i) for i in range(1,33792)] )

    num = 1
    for i in tqdm(range(1,33792)):
        #print(sql_out[num])
        rows_avg_v = mysql.limit_calc_avg(i)
        #print(rows_avg_v)
