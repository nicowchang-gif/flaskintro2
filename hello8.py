from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# create a flask instance
app = Flask(__name__)

# add database
# /// is relative //// is absolute path
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskintro2.db'  

# do not track modification to reduce overhead
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TBD:create a secret_key in a environmental varible
app.config['SECRET_KEY'] = "secret key"

# intiaize the database
db = SQLAlchemy(app)

# create a model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string representation
    def __repr__(self):
    	return f"<Task id={self.id%r}, name={self.name%r}, email={self.email%r}>"


# 1) create a form class -- we need a secret key prior to this
# 2) create a web page - xxx.html 
# 3) create a route + render_template 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	submit = SubmitField("Submit")



# create a form class -- we need a secret key first
class NamerForm(FlaskForm):
	name = StringField("What's your name?", validators=[DataRequired()])
	submit = SubmitField("Submit")



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
@app.route('/user/<name>')
def user(name):
	return render_template("user.html", name=name)


# localhost:5000/user/add
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Users(name=form.name.data, email=form.email.data)
			db.session.add(user)
			db.session.commit()

		name = form.name.data
		form.name.data = ''
		form.email.data = ''
		flash("User Added Successfully!")

	our_users = Users.query.order_by(Users.date_created)

	return render_template("add_user.html", name=name, form=form, our_users=our_users)


# create custom error pages
# invalid url
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


# internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


# 1) create a form class -- we need a secret key prior to this
# 2) create a web page - xxx.html 
# 3) create a route + render_template 
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None # None for the first time display
	form = NamerForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")
	return render_template("name.html", name=name, form=form)


