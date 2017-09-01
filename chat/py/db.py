import sqlite3

db_name = "chat.db"


class LogDB:
    def __init__(self):
        self.conn = sqlite3.connect(db_name)

    def check_exist(self):
        cur = self.conn.cursor()
        ret = cur.execute("""
            select count(*) from sqlite_master
            where type='table' and name='log'
        """)
        num, = ret.fetchone()
        return True if num == 1 else False

    def drop(self):
        if self.check_exist():
            cur = self.conn.cursor()
            sql = "drop table log"
            cur.execute(sql)
            self.conn.commit()

    def create(self):
        cur = self.conn.cursor()
        sql = """
            create table log (
                id integer primary key autoincrement,
                message varchar(100),
                display_id varchar(100),
                post_time timestamp
                )
             """
        cur.execute(sql)
        self.conn.commit()

    def insert(self, message, display_id, post_time):
        cur = self.conn.cursor()
        sql = "insert into log(message, display_id, post_time) values (?, ?, ?)"
        cur.execute(sql, (message, display_id, post_time))
        self.conn.commit()

    def select_all(self):
        cur = self.conn.cursor()
        sql = "select * from log order by id"
        return cur.execute(sql).fetchall()

    def close(self):
        self.conn.close()
        print("db connection closed")


class UserDB:
    def __init__(self):
        self.conn = sqlite3.connect(db_name)

    def check_exist(self):
        cur = self.conn.cursor()
        ret = cur.execute("""
            select count(*) from sqlite_master
            where type='table' and name='users'
        """)
        num, = ret.fetchone()
        return True if num == 1 else False

    def drop(self):
        if self.check_exist():
            cur = self.conn.cursor()
            sql = "drop table users"
            cur.execute(sql)
            self.conn.commit()

    def create(self):
        cur = self.conn.cursor()
        sql = """
            create table users (
                id integer primary key autoincrement,
                user_id varchar(200),
                display_id varchar(100),
                registration_time timestamp
                )
             """
        cur.execute(sql)
        self.conn.commit()
 
    def insert(self, user_id, display_id, registration_time):
        cur = self.conn.cursor()
        sql = "insert into users (user_id, display_id, registration_time) values (?, ?, ?)"
        cur.execute(sql, (user_id, display_id, registration_time))
        self.conn.commit()

    def get_display_id(self, user_id):
        cur = self.conn.cursor()
        sql = "select display_id from users where user_id = ?"
        cur.execute(sql, (user_id,))
        ret = cur.fetchone()
        if ret is None:
            return False
        display_id, = ret
        return display_id

    def close(self):
        self.conn.close()
        print("db connection closed")

