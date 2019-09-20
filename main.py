import os
import pymysql
from datetime import datetime,timedelta
import hashlib
import base64
import pyotp
import requests
import json
from flask import Flask, request, redirect, url_for, render_template, flash
app = Flask(__name__)
def sesame_getter(code):
    db = pymysql.connect(
      host='153.126.197.42',
      user='testuser',
      password='knct0wireless',
      db='sesame_list',
      charset='utf8',
      cursorclass=pymysql.cursors.DictCursor
  )
    cur = db.cursor()
    sql = "select sesame_id from  sesame  where point_code='"+code+"';"
    cur.execute(sql)
    data = cur.fetchall()
    db.close()
    if len(data)==0:
        return "not found"
    else :
        return data[0]["sesame_id"]

def Sesame_lock( sesame_id , check_flag=False ):
        url = "https://api.candyhouse.co/public/sesame/" + sesame_id
        head = {"Authorization":"oOhiMX2DRqKuIX-ChfhtSZV4Vl0A_tLoKQNTwLnEOy98QphUQ6FVAGTNFXCXVWubj34G2h5Zech3"}
        response = requests.get(url, headers=head)

        #now state
        status = response.json()["locked"]
        if status is True :
                return "Error code"

        payload_control = {"command":"lock"}
        response = requests.post( url, headers=head, data=json.dumps(payload_control))

        #Exception handling
        if check_flag is True:
                time.sleep(15)
                task_id = response.json()["task_id"]
                url = "https://api.candyhouse.co/public/action-result?task_id="+task_id
                response = requests.get(url, headers=head)
                if response.json()["successful"]==False :
                        return "Error code Retry!!"

        return "OK"


def create_otp(token):
    data = base64.b32encode( token.encode("UTF-8") )
    totp = pyotp.TOTP(data)
    return totp.now()   #この地点での　情報

def token_check(otp,code):
  tm=datetime.now()+timedelta(hours=9)
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
    return "予約データなし"
 
  ans_otp=create_otp(data[0]["token"])
  print(ans_otp)
  if ans_otp!=otp:
    return "不正な値です"
  else :
    sql="update "+code+" set  act='1'  where  date='"+now+"';"
    cur.execute(sql)
    db.commit()
    sesame_id=sesame_getter(code)
    return Sesame_lock( sesame_id)
  db.close()


@app.route('/token_checker', methods=['GET', 'POST'])
def token_checker():
        if request.method == 'POST':
                otp=request.form["otp"]
                code=request.form["code"]

                
                return token_check(otp,code) 

        return (datetime.now()+timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S") 


if __name__ == "__main__":
        port = int(os.environ.get('PORT', 8080))
        app.run(host ='0.0.0.0',port = port)
