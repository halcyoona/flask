from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

#Init app
app = Flask(__name__)


#Config MySQL
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'myflaskapp'
app.config["MYSQL_CURSORCLASS"] = 'DictCursor'

#init MYSQL
mysql  = MySQL(app)


# Articles = Articles()

#index
@app.route("/")
def index():
	return render_template("home.html") 

#about
@app.route('/about')
def about():
	return render_template('about.html')
# articles
@app.route('/articles')
def articles():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM articles")
	articles = cur.fetchall()
	if result > 0:
		return render_template('articles.html', articles=articles)
	else:
		msg = "No Article Found"
		return render_template('articles.html', msg= msg)

	cur.close()


# single article
@app.route('/article/<string:id>')
def article(id):
	cur = mysql.connection.cursor()

	resutl = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
	article = cur.fetchone()
	return render_template('article.html', article=article)

# registeration form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username  = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Password do not match')])
    confirm=PasswordField('Confirm Password')




# user register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#Create cursor
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)" ,(name, email, username, password)) 
		

		#commit to db
		mysql.connection.commit()
		
		#close connection
		cur.close()		

		flash("You are now registered and can log in", "success")	
		return redirect(url_for("index"))	


	return render_template('register.html', form=form)


#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		#GET FORM Fields
		username = request.form['username']
		password_candidate = request.form["password"]

		#Create cursor
		cur = mysql.connection.cursor()

		#get user by username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
		if result > 0:
			#get store hash
			data = cur.fetchone()
			password = data["password"]


			#compare passwords
			if sha256_crypt.verify(password_candidate, password):
				#Passed
				session["logged_in"] = True
				session['username'] = username
				flash("you are now logged in ", "success")
				return redirect(url_for('dashboard'))

			else:
				error = 'Password not match'
				return render_template('login.html', error=error)
			cur.close()	
		else:
			error = 'username not found'
			return render_template('login.html', error=error)
	return render_template('login.html')		


# check if user logged in  
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if "logged_in" in session:
			return f(*args, **kwargs)
		else:
			flash("Unauthorized, Please login", "danger")
			return redirect(url_for("login"))
	return wrap


#logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash("you are now logged out", 'success')
	return redirect(url_for('login'))




#dashboard
@app.route("/dashboard")
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM articles")
	articles = cur.fetchall()
	if result > 0:
		return render_template('dashboard.html', articles=articles)
	else:
		msg = "No Article Found"
		return render_template('dashboard.html', msg= msg)

	cur.close()

# Article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body  = TextAreaField('Body', [validators.Length(min=30)])

@app.route("/add_article", methods=["GET", "POST"])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == "POST" and form.validate():
		title = form.title.data
		body = form.body.data
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO articles(title, body, author) VALUES (%s, %s, %s)", (title, body, session['username']))

		mysql.connection.commit()

		cur.close()

		flash("Article Created", "success")
		return redirect(url_for("dashboard"))
	return render_template('add_article.html', form=form)




#Run Server
if __name__ == "__main__":
	app.secret_key='secret123'
	app.run(debug=True)