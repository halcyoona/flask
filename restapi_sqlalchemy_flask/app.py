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
	return render_template("home.html") 


#about
@app.route('/about')
def about():
	return render_template('about.html')



# registeration form
class RegisterForm(Form):
    fname = StringField('First Name', [validators.Length(min=1, max=50)])
    lname  = StringField('Last Name', [validators.Length(min=4, max=25)])
    phone = StringField('Phone', [validators.Length(min=6, max=20)])
    dob = DateField('Date of Birth')
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Password do not match')])
    confirm=PasswordField('Confirm Password')




# user register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		fname = form.fname.data
		lname = form.lname.data
		phone = form.phone.data
		dob = form.dob.data
		email = form.email.data
		password = sha256_crypt.encrypt(str(form.password.data))

		obj = User(fname, lname, password, dob, phone, email)
		#Create cursor
		db.session.add(obj)
		db.session.commit()


		flash("You are now registered and can log in", "success")	
		return redirect(url_for("index"))	


	return render_template('register.html', form=form)


# Product Class/Model
# class Product(db.Model):
# 	"""docstring for Product"""
# 	__tablename__="product"
# 	id = Column(Integer, primary_key=True)
# 	name = Column(String(100), unique=True)
# 	description = Column(String(200))
# 	price = Column(Integer)
# 	qty = Column(Integer)

# 	def __init__(self, name, description, price, qty):
# 		self.name = name
# 		self.description = description
# 		self.price = price
# 		self.qty = qty











# # Product Schema
# class ProductSchema(ma.Schema):
# 	class Meta:
# 		fields = ("id", "name", "description", "price", "qty")




# #Init Schema
# product_schema = ProductSchema(strict=True)
# products_schema = ProductSchema(many=True, strict=True)



#Run Server
if __name__== "__main__":
	#set logging
	app.config['SECRET_KEY'] = "Mehmood"
	logging.basicConfig()
	logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
	app.run(debug=True)