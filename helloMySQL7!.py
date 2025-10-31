# declare html auxiliary
import dataclasses
from flask import Flask, render_template, flash, request

# declare flask form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired

# declare sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# declare Migrate
from flask_migrate import Migrate

# declare uitlity
from datetime import datetime


# create a flask instance
app = Flask(__name__)


# add databases
#
# SQLite
# /// is relative //// is absolute path
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskintro2.db'

# MySQL 
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/db_name'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQLPassword@localhost/mysql_flaskintro2'  

# do not track modification to reduce overhead
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# MUST create a secret key first to use FlaskForm
# TBD:store the secret_key in an environmental varible
app.config['SECRET_KEY'] = "secret key"

# intiaize the database
db = SQLAlchemy(app)

# migrate database
migrate = Migrate(app, db)

# create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string representation
    def __repr__(self):
    	return f"<Task id={self.id%r}, name={self.name%r}, email={self.email%r},favorite_color={self.favorite_color%r}>"



# 1) create a form class -- we need a secret key prior to this
# 2) create a web page - xxx.html 
# 3) create a route + render_template 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	submit = SubmitField("Submit")


# localhost:5000/user/add
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Users(name=form.name.data, email=form.email.data,
				favorite_color=form.favorite_color.data)
			db.session.add(user)
			db.session.commit()

		name = form.name.data
		
		form.name.data = ''
		form.email.data = ''
		form.favorite_color.data = ''
		flash("User Added Successfully!")

	our_users = Users.query.order_by(Users.date_created)

	return render_template("add_user.html", name=name, form=form, our_users=our_users)


# update a database record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	record_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		record_to_update.name = request.form['name']
		record_to_update.email = request.form['email']
		record_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html", 
			form=form,
			record_to_update = record_to_update)

		except:
			flash("Error: There was a problem. Try it again!")
			return render_template("update.html", 
			form=form,
			record_to_update = record_to_update,
			id=id)

	else:
		return render_template("update.html", 
		form=form,
		record_to_update = record_to_update)

# delete a database record
@app.route('/delete/<int:id>')
def delete(id):
	record_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(record_to_delete)
		db.session.commit()
		flash("User Deleted Successfully!")
		return render_template("add_user.html", 
		form=form,
		name=name,
		record_to_delete = record_to_delete)

	except:
		flash("Error: There was a problem. Deleting a user!")
		return render_template("add_user.html", 
		form=form,
		name=name,
		record_to_delete = record_to_delete)

# 1) create a form class -- we need a secret key prior to this
# 2) create a web page - xxx.html 
# 3) create a route + render_template 
class NamerForm(FlaskForm):
	name = StringField("What's your name?", validators=[DataRequired()])
	submit = SubmitField("Submit")


# create a name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None # None for the first time display
	form = NamerForm()
	if form.validate_on_submit():
		#same as: name = request.form['name'] ~~ name = form.name.data
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")
	return render_template("name.html", name=name, form=form)



# integrate db during startup
#
# @app.before_first_request
#def nitialize_database():
#	db.create_all()
#

# create a route decorator
@app.route('/')
#def index():
#	return "<h1>Hello World</h1>"
def index():

	first_name = "John"
	stuff = "This is <strong>Bold</strong> type"
	favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template("index.html", first_name=first_name, 
		stuff=stuff, favorite_pizza=favorite_pizza)


# localhost:5000/user/<name>
@app.route('/user/<string:name>')
def user(name):
	return render_template("user.html", name=name)


# create custom error pages
# invalid url
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


# internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


