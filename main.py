import os
import pymysql
from datetime import datetime,timedelta
import hashlib

from flask import Flask, request, redirect, url_for, render_template, flash
app = Flask(__name__)
def token_check(otp,code):
  tm=datetime.now()
  tm = tm - timedelta(minutes=tm.minute % 30,
                             seconds=tm.second,
                             microseconds=tm.microsecond)
  now = tm.strftime("%Y/%m/%d %H:%M:%S") #30分　丸める
  db = pymysql.connect(
      host='153.126.197.42',
      user='testuser',
      password='knct0wireless',
      db='point_code',
      charset='utf8',
      cursorclass=pymysql.cursors.DictCursor
  )
  cur = db.cursor()
  sql = "select token from  "+code+" where  date='"+now+"';"
  cur.execute(sql)
  data = cur.fetchall()
  if len(data)==0:
    return "-2" #予約データなし
  ans_otp=create_otp(data[0]["token"])
  db.close()
  if ans_otp!=otp:
    return "-1" #不正な値です
  else :
    return "0"    #認証ok



@app.route('/token_checker', methods=['GET', 'POST'])
def token_checker():
        if request.method == 'POST':
                otp=request.form["otp"]
                code=request.form["code"]

                
                return token_check(otp,code) 

        return datetime.now().strftime("%Y/%m/%d %H:%M:%S") 


if __name__ == "__main__":
        port = int(os.environ.get('PORT', 8080))
        app.run(host ='0.0.0.0',port = port)
