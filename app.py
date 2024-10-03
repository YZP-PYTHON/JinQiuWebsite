
import random
from datetime import datetime
#from crypt import methods
from random import randint
from urllib import request
import pymysql
from flask import Flask, render_template, request, make_response,redirect

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask_mail import Mail, Message
import json

def yzm(lenth):
    y=0
    for i in range(lenth):
        a=randint(0,9)
        y=y+a
        y=y*10
    return y


json_file_path="config.json"
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)


s = URLSafeTimedSerializer(str(random.randint(100000,1919810)))  # 替换为你的密钥


def generate_token(email, salt, expiration=3600):  # 1小时过期
    return s.dumps(email, salt=salt,salt_length=8)


def send_email_with_token(email, token):
    msg = Message('Verify your email', sender='yzp2369114@163.com', recipients=[email])
    msg.body = f"您的验证码是: {token}"  # 注意：这只是一个示例，实际上你不应该直接发送令牌
    mail.send(msg)

app = Flask(__name__)
email_config=data['email']
app.config.update(
    MAIL_SERVER=email_config['server'],
    MAIL_PORT=email_config['port'],
    MAIL_USE_SSL=email_config['ssl'],
    MAIL_USERNAME = email_config['mail'],
    MAIL_PASSWORD = email_config['password']
)
mail = Mail(app)
db=data['db']
sql = pymysql.connect(
    user='root',
    password='pp1207-2230',
    host='192.168.3.7',
    database='class',
    port= 3306
    )
yb = sql.cursor()


@app.route('/')
def hello_world():  # put application's code here
    log = request.cookies.get('login')
    sql1='select scr,url from imglist where yn = 1'
    yb.execute(sql1)
    imglist=yb.fetchall()
    sql.commit()

    if log == '1':
        cookie_value = request.cookies.get('uuid')
        sql2 = "SELECT username FROM user WHERE uuid = %s"
        yb.execute(sql2, (cookie_value,))
        un = yb.fetchone()
    else:
        un = (1,)
    return render_template("index.html", login=log, username=un[0],imglist=imglist)


@app.route('/login')
def login():
    '''
    if(username in data and passwors==data[username]):
        lg=1
    else:
        lg=0
    '''
    return render_template("login.html")


@app.route('/logmessage', methods=['POST'])
def logmessage():
    emil = request.form['emil']
    password = request.form['password']

    select_query = "select count(ID) from user where email=%s and password=md5(%s)"
    yb.execute(select_query, [emil, password])
    data = yb.fetchone()
    print(data)
    if data[0] == 1:
        a1 = "SELECT uuid FROM user WHERE email = %s"
        yb.execute(a1, (emil,))
        result = yb.fetchone()
        response = make_response(render_template('login_succed.html'))
        response.set_cookie('uuid', str(result[0]))
        response.set_cookie('login', str(1))
        return response
    else:
        response = make_response(render_template('login_fail.html'))
        response.set_cookie('login', '0')
        return response


@app.route('/singin')
def singin():
    return render_template("singin.html")


@app.route('/singin_message', methods=['POST'])
def singin_message():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    StudyID = request.form.get('StudyID')
    select_query = "select id from user where StudyID=md5(%s)"
    yb.execute(select_query, [StudyID])
    re = yb.fetchone()
    print(re)
    if re:
        a2="UPDATE user SET password=MD5(%s), email=%s, username=%s, uuid= MD5(%s) ,yn=%s WHERE id=%s;"
        uuid=email+password
        print(password,email,username,uuid,re[0])


        yb.execute(a2,[password,email,username,uuid,0,re[0]])
        sql.commit()
        response = make_response(redirect('/email'))
        response.set_cookie('email',email)
        return response

    else:
        return render_template('singin_fail.html')
@app.route('/email',methods=['POST','GET'])
def email():
    return render_template('email.html')
@app.route('/send_email',methods=['POST','GET'])
def send():
    email=request.form.get('email')
    code=yzm(6)
    msg=Message('Your Verification Code', sender=data['email']['mail'], recipients=[email])
    msg.body=f'Your verification code is: {code}'
    mail.send(msg)
    sql1='INSERT INTO yzm (email, text) VALUES (%s, %s)'
    yb.execute(sql1,(email,code,))
    sql.commit()

    return redirect('/yzmyz')
@app.route('/yzmyz')
def yzmyz():
    return render_template('yzmyz.html')
@app.route('/yzm_message',methods=['POST'])
def yzm_messang():
    #global time1
    time1=None
    yzm1=request.form.get('yzm')
    email=request.form.get('email')
    sql1='select yn,creat_time from yzm where email=%s and text=%s'
    yb.execute(sql1,(email,yzm1))
    ans=yb.fetchone()
    sql.commit()
    if ans is not None:

        now=datetime.now()
        ytime=ans[1]
        time1= (now-ytime).total_seconds()
        print(str(time1))
    else:
        return redirect('/yzm_fail')
    if ans is None:
        return redirect('/yzm_fail')
    elif time1 is not None and time1 <= 360:
        sql2='update yzm set yn = 1 where email=%s and text=%s'
        yb.execute(sql2,(email,yzm1))
        sql.commit()
        print(ans, email, yzm1,time1)
        sql3='update user set yn = 1 where email=%s'
        yb.execute(sql3,(email,))
        sql.commit()

        return redirect('/yzm_succeed')
    else:
        return 'err'
@app.route('/yzm_fail')
def yzm_fail():
    return render_template('yzm_fail.html')
@app.route('/yzm_succeed')
def yzm_succeed():
    return render_template('yzm_succeed.html')







if __name__ == '__main__':
    app.run(port=80,debug=True)
