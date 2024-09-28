
import random
from crypt import methods
from urllib import request
import pymysql
from flask import Flask, render_template, request, make_response,redirect

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask_mail import Mail, Message
import json

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

    if log == '1':
        cookie_value = request.cookies.get('uuid')
        sql = "SELECT username FROM user WHERE uuid = %s"
        yb.execute(sql, (cookie_value,))
        un = yb.fetchone()
    else:
        un = (1,)
    return render_template("index.html", login=log, username=un[0])


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
        response.set_cookie('first_time',"1")
        return response

    else:
        return render_template('singin_fail.html')
@app.route('/email',methods=['POST','GET'])
def email():
    return render_template('email.html')
@app.route('/send_email',methods=['POST','GET'])
def send():







if __name__ == '__main__':
    app.run(port=80,debug=True)
