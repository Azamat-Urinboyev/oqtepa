from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import sqlite3


class Database:
    def __init__(self, db_name="data/oqtepa_lavash.db") -> None:
        self.db_name = db_name
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.conn

    def create_tables(self):
        users_table = """CREATE TABLE IF NOT EXISTS users(
        id BIGINT NOT NULL,
        username VARCHAR(255) NOT NULL,
        phone_number VARCHAR(255) NOT NULL,
        branch VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
        )"""
        complaint_table = """CREATE TABLE IF NOT EXISTS complaints(
        user_id BIGINT NOT NULL,
        complaint TEXT NOT NULL,
        date DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id)
        )"""

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(users_table)
        cursor.execute(complaint_table)
        conn.commit()
        conn.close()
        print("Database is set up.")
        
    def insert_user(self, user_id, username, phone_number, branch):
        conn = self.connect()
        cursor = conn.cursor()
        sql_query = "INSERT INTO users (id, username, phone_number, branch) VALUES (?, ?, ?, ?)"
        cursor.execute(sql_query, (user_id, username, phone_number, branch))
        conn.commit()
        conn.close()

    def insert_complaint(self, user_id, complaint):
        conn = self.connect()
        cursor = conn.cursor()
        sql_query = "INSERT INTO complaints (user_id, complaint, date) VALUES (?, ?, date('now'))"
        cursor.execute(sql_query, (user_id, complaint))
        conn.commit()
        conn.close()

    def check_user_exist(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        sql_query = "SELECT * FROM users WHERE id=?"
        cursor.execute(sql_query, (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def select_complaints(self, months=1, custom_time=False):
        current_time = datetime.now()
        time = current_time - relativedelta(months=months)
        if custom_time:
            time = custom_time

        conn = self.connect()
        cursor = conn.cursor()
        sql_query = """SELECT u.username,
                                u.phone_number,
                                u.branch,
                                c.complaint,
                                c.date
                        FROM users u JOIN complaints c
                        ON u.id = c.user_id
                        WHERE c.date >= ?
                        ORDER BY c.date"""
        cursor.execute(sql_query, (time, ))
        data = cursor.fetchall()
        conn.close()
        columns = ["ism_familiya", "telefon_raqam", "fillial", "shikoyat", "sana"]
        df = pd.DataFrame(data=data, columns=columns)
        # df["sana"] = df["sana"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        # df["sana"] = pd.to_timedelta(df["sana"])
        return df