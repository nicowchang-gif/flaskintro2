from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired

# create a flask instance
app = Flask(__name__)

# TBD:create a secret_key in a environmental varible
app.config['SECRET_KEY'] = "secret key"


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


# localhost:5000/user/john
@app.route('/user/<name>')
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


# create a form class -- we need a secret key first
class NamerForm(FlaskForm):
	name = StringField("What's your name?", validators=[DataRequired()])
	submit = SubmitField("Submit")


# create a name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None # None for the first time display
	form = NamerForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")
	return render_template("name.html", name=name, form=form)


