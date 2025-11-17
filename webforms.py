
# declare flask form
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, ValidationError, 
	PasswordField, BooleanField, TextAreaField)
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


# 1) create a form class -- we need a secret key prior to this
# 2) create a web page - xxx.html 
# 3) create a route + render_template 



# create a Search Form 
class SearchForm(FlaskForm):

	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")



# create a Login Form to pass in the parameters to route and html page
class LoginForm(FlaskForm):

	username = StringField("User Name", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])

	submit = SubmitField("Submit")



# create a Blog Post Form to pass in the parameters to route and html page
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	##- content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	content = CKEditorField('Content', validators=[DataRequired()])
	##- author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug")

	submit = SubmitField("Submit")



# create a UserForm
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("User Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	about_author = TextAreaField("About Author")
	password_hash = PasswordField("Password", 
				validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
	profile_pic = FileField("Profile pic")

	submit = SubmitField("Submit")

# create a NamerForm
class NamerForm(FlaskForm):
	name = StringField("What's your name?", validators=[DataRequired()])
	submit = SubmitField("Submit")


# create a password Form
class PasswordForm(FlaskForm):
	email = StringField("What's your email?", validators=[DataRequired()])
	password_hash = PasswordField("What's your password?", validators=[DataRequired()])
	submit = SubmitField("Submit")
