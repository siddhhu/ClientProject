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
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer

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
    
with open('file.txt','r') as file:
    conversation = file.read()

bott = ChatBot("Academics ChatBot")
trainer2 = ListTrainer(bott)
trainer2.train([ "Hey",
    "Hi there!",
    "Hi",
    "Hi!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome.",
    "What is your name?", "My name is Academics ChatBot",
    "Who created you?", "Chenna",
    "What is this platform for?",
    "It is an end to end application to communicate with faculty & student ",
    "Email : niretichennakeshva@gmail.com, Mobile number : +91 6300724393 Location : Pune, Maharashtra",
    "Education",
    "Bachelor of Engineering (B.E), Computer Science & Engineering\n Pune Vidyarthi Grihas College Of Engineering And Technology Pune '\n'2018 - 2022 '\n'CGPA: 8.84/10 '\n'Senior Secondary (XII), Science Sir Parashurambhau College Pune Maharashtra (MAHARASHTRA STATE BOARD board) Year of completion: 2018 Percentage: 88.40% Secondary (X) Sant Meera School Aurangabad (MAHARASHTRA STATE BOARF board) Year of completion: 2016 Percentage: 96.20%",
    "Projects",
    "Course Available in College?", "B.Tech, BCA, MCA, MBA & M.Tech",
    "Do we have Library Facaility?", "Yes we do have a good library with 100 of rooms where you can do self study. ",
        "Placement record of the college", "We have placement. A lot of companies are visting in our campus like wipro, Cognizant & Infosys with around 90 % placement records.",
                "College Name", "Siddhartha Institue of technogy"
    
    ])
trainer = ChatterBotCorpusTrainer(bott)
trainer.train("chatterbot.corpus.english")
#trainer2.train(["Thank You","Welcome"])



@app.route("/get")
def get_bot_response():
	userText = request.args.get('msg')
	return str(bott.get_response(userText))
@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method=="GET":
	    return render_template('game.html')
    if request.method=="POST" :
        username=request.form.get('username')
        user=User.query.filter_by(username=username).first()
        session["user"]=user.username
        session["type"]=user.type
        print("This is user type"+user.type)
        if user and user.type=='student':
            return redirect("/welcome")
        else:
            return redirect("admin")
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
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password,type=type)
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