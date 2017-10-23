import sqlite3 as lite
import datetime


logd = (
    ('DLM', datetime.datetime.now().__str__(), '0', 'FIRSTONE', 'OK', 'test', '0')
)

con = lite.connect('db.sqlite3')


with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS logdata")
    cur.execute("CREATE TABLE logdata ("
                " `currency` TEXT NOT NULL,"
                " `datetime` datetime NOT NULL,"
                " `amount` REAL NOT NULL,"
                " `description` TEXT NOT NULL,"
                " `result_pay` TEXT,"
                " `pay_way` TEXT,"
                " `shop_invoice_id` INT NOT NULL )")
    print(logd)
    #cur.executemany("INSERT INTO logdata VALUES (?, ?, ?, ?, ?)", logd)
    cur.execute("INSERT INTO logdata VALUES (?, ?, ?, ?, ?, ?, ?)", logd)
