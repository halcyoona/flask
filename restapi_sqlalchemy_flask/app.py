from flask import Flask, jsonify
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from database import User, Email, Draft, Inbox, Sentbox
import logging
import os





#init app
app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))



#Datebase
# username = "root"
# password = ""
# database = "myapp"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{0}:{1}@localhost/{3}',(username, password, database)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'myapp.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# app.config["MYSQL_HOST"] = 'localhost'
# app.config["MYSQL_USER"] = 'root'
# app.config["MYSQL_PASSWORD"] = ''
# app.config["MYSQL_DB"] = 'myapp'


#Init db
db = SQLAlchemy(app)


# Init ma
# ma = Marshmallow(app)

# index
@app.route("/")
def index():
	return render_template("index.html") 


#about
@app.route('/help')
def help():
	return render_template('help.html')


# Signin User form
class SigninUser(Form):
    username = StringField("",[validators.Length(min=4, max=50)])


@app.route('/index')
def signin():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		search = User.query.filter_by(username=username).first()
		if search == "":
			flash("User not exist","danger")
		else:
			redirect(url_for("index1"))
	return render_template('index.html')


# Signin Password form
class SigninPass(Form):
    password = StringField("",[validators.Length(min=4, max=50)])

@app.route('/index1')
def signin1():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		password = form.password.data
	return render_template('index1.html')



# registeration form
class RegisterForm(Form):
    fname = StringField("",[validators.Length(min=1, max=50)])
    lname  = StringField('', [validators.Length(min=4, max=25)])
    phone = StringField('', [validators.Length(min=6, max=20)])
    dob = DateField('')
    username = StringField('', [validators.Length(min=6, max=50)])
    password = PasswordField('', [validators.DataRequired(), validators.EqualTo('confirm', message='Password do not match'), validators.Length(min=6)])
    confirm=PasswordField('')




# user register
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		fname = form.fname.data
		lname = form.lname.data
		phone = form.phone.data
		dob = form.dob.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		obj = User(fname, lname, password, dob, phone, username)
		#Create cursor
		db.session.add(obj)
		db.session.commit()


		flash("You are now registered and can log in", "success")	
		return redirect(url_for("index"))	


	return render_template('signup.html', form=form)






#Run Server
if __name__== "__main__":
	#set logging
	app.config['SECRET_KEY'] = "Mehmood"
	logging.basicConfig()
	logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
	app.run(debug=True)