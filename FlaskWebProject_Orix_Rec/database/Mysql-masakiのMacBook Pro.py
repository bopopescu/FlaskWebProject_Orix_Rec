# database
from sqlalchemy import create_engine
import pymysql.cursors
import mysql.connector
import sqlite3

class Mysql:
    def __init__(self, host, db_name, user, pass):
        self.num = num;  #このクラスが持つ「num」変数に引数を格納
        # データベース接続
        """
        con = mysql.connector.connect(
        host='172.31.19.191',
        db='orix_data',
        user='root',
        passwd='0gur11a6'
        )
        cur = con.cursor(dictionary=True)
        """
        self.con = mysql.connector.connect(
        host=host,
        db=db_name,
        user=user,
        passwd=pass'
        )
        self.cur = con.cursor(dictionary=True)


    def sql_excute_fetch(self, sql):
        ##print(sql)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return rows


if __name__ == '__main__':
    mysql = Mysql(host='172.31.19.191', db_name='orix_data', user='root', pass='0gur11a6')
    sql_out =  mysql.sql_excute_fetch()
