from flask import Flask, render_template,session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import os.path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from random import randint
from datetime import datetime
from datetime import date
import sqlite3
import razorpay
from flask import Flask, render_template, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import math
import string
import random
import urllib
import json
import os
from datetime import datetime
import re



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

db_path = os.path.join(os.path.dirname(__file__),'headortails.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'


today = date.today()
now=datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
class Withdraw(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    withdraw = db.Column(db.Integer)
    active_user=db.Column(db.String(120),nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    type = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4,max=25)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    type = StringField('type', validators=[InputRequired(), Length(min=8, max=80)])
    

@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method=="GET":
	    return render_template('game.html')
    if request.method=="POST" :
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username,password=password).first()
        print(user)
        if user is not None and user.type=='student':
            session["user"]=user.username
            session["type"]=user.type
            return redirect("/welcome")
        elif user is not None and user.type=='admin':
            session["user"]=user.username
            session["type"]=user.type
            return redirect("/admin")
        else:
            return render_template("game.html",msg="Incorrect Credentails")
@app.route("/admin")
def admin():
    current_user=session["user"]
    return render_template("notcopy.html",current_user=current_user)
@app.route("/answerquestion")
def answerquestion():
    question=Questions.query.all()
    
    return render_template("answerquestion.html",i=question)

@app.route("/facultyanswered")
def faculty():
    rows=Questions.query.filter_by().all()

    return render_template("faculty.html",rows=rows)

@app.route("/answered",methods=["GET","POST"])  
def answered():
    if request.method=="POST":
        ans=request.form.get("ans")
        print("Empty Ans: ",len(ans))
        if len(ans)==0:
            ans="Question Marked as Invalid!!"
        a_user =Questions.query.all()
        for i in a_user:
            if i.answer==None:
                i.answer=ans
                print("ye hai DB ka Answer",i.answer)
                db.session.commit()
                return render_template("success.html")

@app.route("/ans",methods = ['GET','POST'])
def ans():
    if request.method == 'POST':
        todo_data = request.get_json()
        content=todo_data['userInput']
        content1 = str(content)
        print(content1)
        print("I came to ans")
        answer = chatbot_query(content1)
        return answer
    else:
        return "Din succeed"

def greeting(searchtext):
    #if the user's sentence is some greeting return a randomly chosen greeting response
    robo_response = " "
    with open('/Users/siddhartha/Documents/Development/headandtail-master/json_files/intents.json', 'r') as file1:
        data1 = json.load(file1)

    for intent1 in data1['intents']:
        for pattern1 in intent1['patterns']:
            if pattern1.lower() == searchtext:
                robo_response = random.choice(intent1['responses'])
                break
    return robo_response

# Generate the response
def response(searchtext):
    print("I am in function response")
    count = 0
    robo_response = " "
    str1 = " "
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    searchtext = searchtext.lower().translate(remove_punct_dict)
    #print("Search text is:"+searchtext)
    robo_response = greeting(searchtext)
    if robo_response != "":
        return robo_response
    else:
        with open('/Users/siddhartha/Documents/Development/headandtail-master/json_files/QDas.json', 'r') as file2:
            data = json.load(file2)
            print(data)
        remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        searchtext = searchtext.lower().translate(remove_punct_dict)
        list1 = ["qsstat", "qs stat", "solara","sollara", "procella","procela", "mqis", "m qis","mqs", "oqis","oqs", "o qis", "install", "citrix","citrx","online", "desktop","desktp", "notebook","notebk", "qdas", "q das","qds", "upload","upld", "spc"]
        list2 = ["access","accss","acess", "issue","isue", "problem","prblm", "ticket","tckt", "contact","cntct"]
        print(searchtext)
        for i in list1:
            if (searchtext.find(i) != -1):
                if i == "q das" or i == "qs stat" or i == "m qis" or i == "o qis":
                    i = re.sub('[\s+]', '', i)
                str1 = str1 + i + " "
        for j in list2:
            if (searchtext.find(j) != -1):
                str1 = str1 + j + " "
        str2 = str1[:len(str1) - 1]
        for intent in data['intents']:
            for pattern in intent['patterns']:
                if pattern.lower() == str2:
                    print("1")
                    robo_response = random.choice(intent['responses'])
                    count = 1
                    break

        if count == 1:
            print(robo_response)
            #k = databasetransfer("known", searchtext, robo_response)

        else:
            robo_resp = ["Can you re-frame the sentence with correct grammar. I might be able to answer better", "I am a bit old school and have issues with abbreviations. LOL! Could you please rectify the sentence with any such issue and try again", "Please use Q-Das related terms so that it will be helpful for me to give a better search result for you","Uhmmm.. I am out of answers this time.. Can I interest you in having a look at Q-Das home page. You might find relevant documents there. <a href=https://inside-docupedia.bosch.com/confluence/display/qdas/Q-DAS+Home>Q-Das Home</a>"]
            robo_response = random.choice(robo_resp)
            #k = databasetransfer("unknown", searchtext, robo_response)
        return robo_response

def chatbot_query(user_resp , index=0):
    fallback = 'Sorry, I cannot think of a reply for that.'
    result = ''
    user_res = []
    user_response = str(user_resp)
    user_response = user_response.lower()
    #user_res = user_response.split("'")
    try:
        print("I am in try block")
        print(user_response)
        result = result + ""+response(user_response)
        return result

    except:
        if len(result) == 0:
            result += fallback
        return result
     

@app.route("/invalid",methods=["GET","POST"])
def invalid():
    rows=Questions.query.filter_by().all()

    return render_template("invalidquestion.html",rows=rows)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        email=request.form.get('email')
        type=request.form.get('type')
        new_user = User(username=username, email=email, password=password,type=type)
        db.session.add(new_user)
        db.session.commit()
        print(new_user.email)
        return redirect('/')
    return render_template('sign.html')

# @app.route('/welcome')

# def welcome():
#     new=0
#     active_user=current_user.username
#     connection = sqlite3.connect("headortails.db")
#     cursor = connection.cursor()
#     cursor.execute('SELECT sum(amount) FROM payment where active_user=?',(active_user,))
#     results = cursor.fetchall()
#     # print(results[0])
#     for pay in results:
#         my_wallet=pay[0]
        
#     return render_template('playGame.html',ds=dt_string,ip=IPAddr,res=my_wallet)

class Stats(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Integer,nullable=False)
    date=db.Column(db.String(120),nullable=False)
    flipping=db.Column(db.String(120),nullable=False)
    active_user=db.Column(db.String(120),nullable=False)
    result=db.Column(db.String(120),nullable=False)
    wallet=db.Column(db.Integer,nullable=False)

class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    number=db.Column(db.Integer,nullable=False)
    name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(120),nullable=False)
    message=db.Column(db.String(120),nullable=False)


class History(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    bet_amount=db.Column(db.Integer,nullable=False)
    last_wallet=db.Column(db.Integer,nullable=False)
    date=db.Column(db.String(120),nullable=False)
    your_flipping=db.Column(db.String(120),nullable=False)
    active_user=db.Column(db.String(120),nullable=False)
    result=db.Column(db.String(120),nullable=False)
    

class Updated(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    updated_balance=db.Column(db.Integer,nullable=False)
    available=db.Column(db.Integer,nullable=False)
    active_user=db.Column(db.String(120),nullable=False)


class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(120),nullable=False)
    username=db.Column(db.String(120),nullable=False)
    amount=db.Column(db.String(120),nullable=False)
    active_user=db.Column(db.String(120),nullable=False)
class Questions(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(120),nullable=False)
    doubt=db.Column(db.String(120),nullable=False)
    time=db.Column(db.String(120),nullable=False)
    answer=db.Column(db.String(120),nullable=True)
class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Integer,nullable=False)
    active_user=db.Column(db.String(120),nullable=False) 
    status= db.Column(db.String(120),nullable=False) 
    date=db.Column(db.String(120),nullable=False) 

from datetime import date
today = date.today()
print("Today's date:", today)

    
@app.route('/auth',methods=["GET","POST"])
def auth():
    active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute('SELECT withdraw FROM withdraw order by id desc limit 1')
    results=cursor.fetchall()
    for result in results:
        bet=result[0]
    withdraw=request.form.get('withdraw')
    withdraw1=int(withdraw)
    available=request.form.get('available')
    available1=int(available)
    updated_balance=bet-withdraw1
    user=Updated(updated_balance=updated_balance,active_user=active_user,available=available1)
    db.session.add(user)
    db.session.commit()
    status='Pending'
    user=Admin(amount=withdraw1,active_user=active_user,status=status,date=today)
    db.session.add(user)
    db.session.commit()
    if withdraw1>=25 or available1<0:
        return "You can withdraw maximum $ 25 dollar...Please enter amount less than 25 dollars"
    elif withdraw1>0 and withdraw1<=25 and available1>0 and available1>withdraw1:
        user=Stats(amount=-withdraw1,date=dt_string,flipping=0,active_user=active_user,wallet=0,result=0)
        db.session.add(user)
        db.session.commit()
        return render_template('auth.html',money=withdraw1)
    else:
        return "Something went wrong"


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))
@app.route('/askquestions',methods=["GET","POST"])
def ask():    
    if request.method=="GET":
        active_user=session['user']
        print(active_user)
        return render_template('ask.html', active_user=active_user)
    if request.method=="POST":
        active_user=session["user"]
        doubt=request.form.get("doubt")
        print(doubt)
        time=today
        question=Questions(username=active_user,time=time,doubt=doubt)
        db.session.add(question)
        db.session.commit()   
        print(question.doubt)
        return render_template('ask1.html', active_user=active_user,msg="Your Query has been accepted!!")

@app.route('/welcome',methods=["GET","POST"])
def game(): 
    current_user=session["user"]
    return render_template('not.html',current_user=current_user,type=session["type"])
       

    

        

        

             
               
              
            


@app.route('/home')
def home_page():
    active_user=session["user"]
    question = Questions.query.filter_by(username=active_user).all()
    for i in question:
        print(i.answer)
    return render_template('form3.html',rows=question,active_user=active_user)
@app.route('/faq')
def faq():
    return render_template('faq.html')
@app.route('/contact',methods=["POST","GET"])
def contact():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        number=request.form.get('number')
        message=request.form.get('message')
        user=Contact(name=name,email=email,number=number,message=message)
        db.session.add(user)
        db.session.commit()
        return '<h1 style="text-align:center;padding-top:234px;">You will be contacted soon...<br><br>  Thank you for your time!!!</h1>'
    return render_template('contact.html')



@app.route('/add',methods=['GET','POST'])
def hello():
    if current_user.is_authenticated:
        active_user=current_user.username
        if request.method=="POST":
            email=request.form.get('email')
            username=request.form.get('username')
            amount=request.form.get('amount')
            user=Payment(email=email,username=username,amount=amount,active_user=active_user)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('pay',id=user.id))
    return render_template('payment.html')
@app.route('/pay/<id>',methods=['GET','POST'])
def pay(id):
    user=Payment.query.filter_by(id=id).first()
    client=razorpay.Client(auth=("rzp_test_pQ6vOVhgjH2X8K","uTyrej8CdKIf6lzgll8VYAmJ"))
    payment=client.order.create({'amount': (int(user.amount)*100),'currency':'INR','payment_capture':'1'})
    return render_template('RazorPay.html',payment=payment)

@app.route('/success',methods=['GET','POST'])
def success():
    if current_user.is_authenticated:
        active_user=current_user.username
    connection = sqlite3.connect("headortails.db")
    cursor = connection.cursor()
    cursor.execute("SELECT amount FROM payment where active_user=active_user")
    results = cursor.fetchall()
    return render_template('success.html',results=results)

if __name__ == "__main__":
    app.debug=True
    db.create_all()
    app.run()
    FLASK_APP=app.py