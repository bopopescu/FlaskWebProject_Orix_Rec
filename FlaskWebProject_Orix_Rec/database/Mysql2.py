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

import numpy as np

from . import Mysql2

# データベース接続
con = mysql.connector.connect(
host='172.31.19.191',
db='orix_data',
user='root',
passwd='0gur11a6'
)
cur = con.cursor(dictionary=True)

def mysql_sample_multi(id):

    try:
        cur.execute('SELECT * FROM `limit_velocity` WHERE  id = ' + str(id))
        rows = cur.fetchall()

        sql_avg_v = 'SELECT  AVG(velocity_kmh) FROM `Drive_recorder` WHERE ' + str(rows[0]['longitude']) + ' = CAST(`longitude`*1000 AS INT)/1000  AND ' + str(rows[0]['latitude']) + '=  CAST(`latitude`*1000 AS INT)/1000 AND velocity_kmh > 20'
        cur.execute(sql_avg_v)
        rows_avg_v = cur.fetchall()

        sql = "UPDATE `limit_velocity` SET velocity_avg=" + str(rows_avg_v[0]['AVG(velocity_kmh)']) + " WHERE id=" + str(id)
        #self.cur.execute(sql)
        #self.con.commit()
        cur.execute(sql)
        con.commit()
        return -1

    except:
        return -1

class Mysql2:
    def __init__(self, host='172.31.19.191', db_name='orix_data', user='root',normal_list_between1=5, normal_list_between2=5, target_sub=1, target_id=10):
        self.con = mysql.connector.connect(
        host=host,
        db=db_name,
        user=user,
        passwd='0gur11a6'
        )
        self.cur = self.con.cursor(dictionary=True)
        self.sql_out = []
        self.normal_list_between1=normal_list_between1
        self.normal_list_between2=normal_list_between2
        self.target_sub = target_sub
        self.target_id = target_id
        self.normal_v = []
        self.normal_v_len = []
        self.normal_type = []
        self.target_normal_time = []
        self.notmal_target_info = []
        self.target_table = []
        #self.target_id = []
        self.normal_v_list = []
        self.g_box = []

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
        #sql_max_v = 'SELECT  MAX(velocity_kmh) FROM `Drive_recorder` WHERE ' + str(rows[0]['longitude']) + ' = CAST(`longitude`*1000 AS INT)/1000  AND ' + str(rows[0]['latitude']) + '=  CAST(`latitude`*1000 AS INT)/1000 AND velocity_kmh > 20'
        rows_avg_v =  mysql.sql_excute_fetch(sql_avg_v)
        sql = "UPDATE `limit_velocity` SET velocity_avg=" + str(rows_avg_v[0]['AVG(velocity_kmh)']) + " WHERE id=" + str(num)
        #self.cur.execute(sql)
        #self.con.commit()
        self.cur.execute(sql)
        self.con.commit()
        print()
        return rows_avg_v

    def indi_regist(self, sql):
        self.cur.execute(sql)
        self.con.commit()

    def get_v(self):
        target_normal_time = str(self.notmal_target_info['DATE'])
        normal_list_sql = "select * from `Drive_recorder` WHERE `DATE` BETWEEN ('" + target_normal_time + "' - INTERVAL " + str(self.normal_list_between1) + " SECOND) AND ('" + target_normal_time + "' + INTERVAL " + str(self.normal_list_between2) + " SECOND) AND sub = " + str(self.target_sub)
        normal_v_list =  mysql.sql_excute_fetch(normal_list_sql)
        #print(normal_list_sql)
        #print(normal_v_list)
        normal_v = []
        for i in range(len(normal_v_list)):
            normal_v.append(normal_v_list[i]['velocity_kmh'])
        #print(normal_v)

        self.normal_v_list = normal_v_list
        self.target_normal_time = target_normal_time
        self.normal_v = normal_v
        self.normal_v_len = len(normal_v)
        self.delta_v = normal_v[0] - normal_v[-1]
        self.normal_type = 1 if self.delta_v < 0 else -1
        #self.latitude	=

    def regist_row(self, regist_name, regist_value):
        sql = "INSERT INTO `"+self.target_table+"` (id, `" +regist_name+ "`) VALUES ("+str(self.target_id)+", '"+regist_value+"') ON DUPLICATE KEY UPDATE `" +regist_name+ "` = VALUES (`" +regist_name+ "`)";
        #sql = "UPDATE " + target_table + " SET " + regist_name + " = " + regist_value + " WHERE id=" + str(id)
        #print("sql")
        #print(sql)
        self.cur.execute(sql)
        self.con.commit()

    def regist_row2(self, regist_name1, regist_value1, regist_name2, regist_value2):
        #sql = "INSERT INTO `"+self.target_table+"` (id, `" +regist_name1+ "`, `" +regist_name2+ "`) VALUES ("+str(self.target_id)+", '"+regist_value1+"', '"+regist_value2+"') ON DUPLICATE KEY UPDATE `" +regist_name1+ "`, `" +regist_name2+ "` = VALUES (`" +regist_name1+ "`, `" +regist_name2+ "`)";
        sql = "INSERT INTO `"+self.target_table+"` (id, `" +regist_name1+ "`, `" +regist_name2+ "`) VALUES ("+str(self.target_id)+", '"+regist_value1+"', '"+regist_value2+"') ON DUPLICATE KEY UPDATE `" +regist_name2+ "` = VALUES (`" +regist_name2+ "`)";
        #sql = "UPDATE " + target_table + " SET " + regist_name + " = " + regist_value + " WHERE id=" + str(id)
        #print("sql")
        #print(sql)
        self.cur.execute(sql)
        self.con.commit()

    def regist_init(self, target_table):
        self.target_table = target_table

    def regist_normal_list(self):
        mysql.regist_init('normal_list')
        mysql.regist_row('DATE', str(self.notmal_target_info['DATE']))
        mysql.regist_row('sub', str(self.notmal_target_info['sub']))
        mysql.regist_row('latitude', str(self.notmal_target_info['latitude']))
        mysql.regist_row('longitude', str(self.notmal_target_info['longitude']))
        mysql.regist_row('type', str(self.normal_type))
        mysql.regist_row('delta_v', str(self.delta_v))
        mysql.regist_row('t_period', str(self.normal_v_len))
        #print(type(self.g_box))
        mysql.regist_row('g_max', str(max(self.g_box)))
        mysql.regist_row('g_min', str(min(self.g_box)))

    def regist_normal_list_v(self):
        mysql.regist_init('normal_list_v')
        for i, row_info in enumerate(self.normal_v_list, 1):
            #print(row_info['DATE'])
            #print(self.notmal_target_info['DATE'])
            if(str(row_info['DATE']) == str(self.notmal_target_info['DATE']) ):
                mysql.regist_row2('t', str(i), 'target_flag', str(1))
            else:
                mysql.regist_row2('t', str(i), 'target_flag', str(0))
            mysql.regist_row2('t', str(i), 'DATE', str(row_info['DATE']))
            mysql.regist_row2('t', str(i), 'v', str(row_info['velocity_kmh']))
            mysql.regist_row2('t', str(i), 'latitude', str(row_info['latitude']))
            mysql.regist_row2('t', str(i), 'longitude', str(row_info['longitude']))

            if(i>1):
                a_m_ss = float(self.normal_v_list[i-1]['velocity_kmh'] - self.normal_v_list[i-2]['velocity_kmh'])/3.6
                mysql.regist_row2('t', str(i), 'a', str(a_m_ss))
                mysql.regist_row2('t', str(i), 'g', str(a_m_ss/9.8))
                self.g_box.append(a_m_ss/9.8)

        #sql = "UPDATE `normal_list` SET `DATE`='" + str(self.notmal_target_info['DATE']) + "', sub= " + str(self.notmal_target_info['sub']) + "WHERE id=" + str(self.notmal_target_info['id'])
        #self.cur.execute(sql)
        #self.con.commit()

    def get_notmal_target_info(self, id):
        normal_list_sql = "select * from `Drive_recorder` WHERE id = " + str(id)
        self.notmal_target_info =  mysql.sql_excute_fetch(normal_list_sql)[0]
        #print(self.notmal_target_info)


    def create_normal_list(self):
        #print(mysql)
        #print(self.target_id)
        #mysql = Mysql2(host='172.31.19.191', db_name='orix_data', user='root',normal_list_between1=5, normal_list_between2=5, target_sub=1, target_id=10)
        mysql.get_notmal_target_info(self.target_id)
        mysql.get_v()
        mysql.regist_normal_list_v()
        mysql.regist_normal_list()

if __name__ == '__main__':

    mysql = Mysql2(host='172.31.19.191', db_name='orix_data', user='root',normal_list_between1=5, normal_list_between2=5, target_sub=1, target_id=10)
    mysql.create_normal_list()



    aaa
    mysql.get_v(target_normal_time)
    mysql.regist_normal_list()


    limit_velocity_list = mysql.sql_excute_fetch('SELECT * FROM `limit_velocity` WHERE sub = 1')

    lv_id_list = []
    for i in ids:
        lv_id_list.append(limit_velocity_list[i]['id'])



    r = Parallel(n_jobs=30)( [delayed(mysql_sample_multi)(i) for i in id_list] )

    pool = Pool(processes=30)
    with tqdm(total=len(id_list)) as t:
        for _ in pool.imap_unordered(mysql_sample_multi, id_list):
            t.update(1)
    aaa
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



    num = 1
    for i in tqdm(range(1,33792)):
        #print(sql_out[num])
        rows_avg_v = mysql.limit_calc_avg(i)
        #print(rows_avg_v)
