from flask import Flask, render_template, request, json, redirect, url_for
from flask import g
import requests
import sqlite3
import hashlib
import datetime


app = Flask(__name__, static_url_path='')
app.config.from_object(__name__)
app.database = 'db.sqlite3'

def create_shop_invoice_id():
    g.db = connect_db()
    cur = g.db.execute('SELECT max(shop_invoice_id) FROM logdata')
    rows = cur.fetchone()
    g.db.close()
    print('max='+rows[0].__str__())
    return rows[0]

def getlog():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM logdata')
    log = [dict(currency=row[0],
                datetime=row[1],
                amount=row[2],
                description=row[3],
                result_pay=row[4],
                pay_way=row[5],
                shop_invoice_id=row[6])
           for row in cur.fetchall()]
    g.db.close()
    return log

@app.route('/', methods=['GET', 'POST'])
def index():
    #print("new invoiceid="+(int(create_shop_invoice_id())+1).__str__())

    if request.method == 'POST':
        amount = request.form['amount1']
        description = request.form['description1']
        currency = 840
        result_pay = '?'
        #id_pay = int(create_shop_invoice_id())+1
        payway = 'trio_usd'
        shop_id = 305139
        secret = 'gEQSSv19ujyO1i4BhCCw18dRFXP884QMH'
        shop_invoice_id = (int(create_shop_invoice_id())+1).__str__()
        if request.form['currency1'] == 'USD':
            linegen = amount.__str__() + \
                      ':' + currency.__str__() + \
                      ':' + shop_id.__str__() + \
                      ':' + 'desity'+shop_invoice_id + secret
            req = hashlib.md5()
            req.update(linegen.encode("UTF-8"))
            g.db = connect_db()
            logd = (
                (currency.__str__(),
                    datetime.datetime.now().__str__(),
                    amount.__str__(),
                    description,
                    result_pay,
                    payway,
                    shop_invoice_id
                 )
                    )
            g.db.execute("INSERT INTO logdata VALUES(?, ?, ?, ?, ?, ?, ?)", logd)
            g.db.commit()
            g.db.close()
            print(logd)
            print('sign:' + req.hexdigest())

            #return redirect(url_for('pay_button'))

            return render_template('1.html',
                                   amount=amount,
                                   currency=currency,
                                   payway=payway,
                                   shop_id=shop_id,
                                   sign=req.hexdigest(),
                                   shop_invoice_id='desity'+shop_invoice_id)

        if request.form['currency1'] == 'EUR':
           payway='payeer_eur'
           linegen = amount.__str__() + \
                     ':' + currency.__str__() + \
                     ':' + payway + \
                     ':' + shop_id.__str__() + \
                     ':' + 'desity'+shop_invoice_id + secret

           req = hashlib.md5()
           req.update(linegen.encode("UTF-8"))
           data = {"description": 'Test invoice',
                         "payway": payway,
                         "shop_invoice_id": 'desity'+shop_invoice_id,
                         "sign": req.hexdigest(),
                         "currency": currency,
                         "amount": amount,
                         "shop_id": shop_id}
           headers = {"Content-Type": "application/json"}
           print(data)
           r = requests.post('https://central.pay-trio.com/invoice',
                             data=json.dumps(data),
                             headers=headers)
           print(r.text)
           if json.loads(r.text)['result'] == 'ok':
               return redirect(json.loads(r.text)['data']['data']['referer'])

           g.db = connect_db()
           logd = (
               (currency.__str__(),
                datetime.datetime.now().__str__(),
                amount.__str__(),
                description,
                json.loads(r.text)['result'],
                payway,
                shop_invoice_id
                )
           )
           g.db.execute("INSERT INTO logdata VALUES(?, ?, ?, ?, ?, ?, ?)", logd)
           g.db.commit()
           g.db.close()
           return render_template('1.html')

    if request.method == 'GET':
        log = getlog()
        return render_template('1.html', log=log)

@app.route('/user/<name>')
def user(name):
    return "hello %s" % name

def connect_db():
    return sqlite3.connect('~/db.sqlite3')


if __name__ == '__main__':
    app.run(debug=True)

