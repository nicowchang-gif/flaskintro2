# declare flask
from flask import Flask, render_template, flash, request, redirect, url_for

# declare flask forms
from webforms import LoginForm, PostForm, UserForm, NamerForm, PasswordForm, SearchForm

# declare login
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# declare utilities
from datetime import datetime, date
from email import message

# declare sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# declare migrate
from flask_migrate import Migrate

# declare werkzeug sec password
from werkzeug.security import generate_password_hash, check_password_hash

# declare werkzeug util -- profile pic
from werkzeug.utils import secure_filename

# declare uuid -- profile pic
import uuid as uuid

# declare os -- profile pic
import os

# declare ckeditor
from flask_ckeditor import CKEditor


# declare JSON
# from flask import jsonify

# debugging
import pdb

# create a flask instance
app = Flask(__name__)

# add ckeditor
ckeditor =CKEditor(app)

# add databases
#
# SQLite
# /// is relative //// is absolute path
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskintro2.db'

# MySQL 
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/db_name'  
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MySQLPassword@localhost/mysql_flaskintro2'  

# Postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ucum8jhn266i98:pe2bb33a8f223e7660eacbd839ea6f61edea34f31832e05c281bb14220e557e4a@c3v5n5ajfopshl.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dd47inm50o3ef1'  

# do not track modification to reduce overhead
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# MUST create a secret key first to use FlaskForm
# TBD:store the secret_key in an environmental varible
app.config['SECRET_KEY'] = "secret key"

# Location holder for saved profile_pic image
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# intiaize the database
db = SQLAlchemy(app)

# migrate database
migrate = Migrate(app, db)


########### SEARCH #############

# create a search page
@app.route('/search', methods=['POST'])
def search():
	
	form = SearchForm()
	# basic query to get all data
	posts = Posts.query
	if form.validate_on_submit():
		
		# get data from sumitted form
		post.searched = form.searched.data
		
		# query the database
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html", form=form, 
			searched = post.searched,
			posts = posts)


# make a helper function available in all templates including navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)


############## LOGIN #############

# declare flask LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


# create a Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# check password hash
			if check_password_hash(user.password_hash, form.password.data):
				# LoginManager function
				login_user(user)

				flash("Login Successfull")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password. Try Again!")
		else:			
			flash("User Does Not Exist. Try Again!")

	return render_template("login.html", form=form)

# create a Logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Are Now Logged Out!")
	return redirect(url_for('login'))

############## POSTS #############

# create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    ##-author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # add a foreign key to link Users (refer to primary key of Users)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# add Post Page
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		
		poster = current_user.id
		post = Posts(title=form.title.data, 
			content=form.content.data,
			##-author=form.author.data,
			poster_id=poster,
			slug=form.slug.data)
		
		# add to database
		db.session.add(post)
		db.session.commit()
		
		# clear the form
		form.title.data = ''
		form.content.data = ''
		##- form.author.data = ''
		form.slug.data = ''

		# return message
		flash("Blog Post Added Successfully!")

	return render_template("add_post.html", form=form)
	

# display Posts Page
@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
	
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


# specific Post Page
@app.route('/posts/<int:id>')
@login_required
def post(id):
	
	post = Posts.query.get_or_404(id)
	return render_template("post.html", post=post)


# Edit Post Page
@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):

	post = Posts.query.get_or_404(id)
	form = PostForm()
	user_id = current_user.id
	if user_id == post.poster_id:
		if form.validate_on_submit():
			
			post = Posts.query.get_or_404(id)
			post.title = form.title.data 
			post.content = form.content.data
			##- post.author = form.author.data
			post.slug = form.slug.data

			post = Posts(title=form.title.data, 
				content=form.content.data,
				# author=form.author.data,
				slug=form.slug.data)
			
			# update database
			### bug - db.session.add(post)
			### for update process, just use commit()
			db.session.commit()

			# return message
			flash("Blog Post Updated Successfully!")		

			# redirect to the webpage
			return redirect(url_for('post', id=id))

		# pre-fill the form
		form.title.data = post.title
		form.content.data = post.content
		form.slug.data = post.slug
		return render_template('edit_post.html', form=form)

	else: 		
		if post:
			flash("You are not authorized to edit that post.  Try again!")	
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)


	flash("You are not authorized to edit that post.  Try again!")	
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


# delete Post Page
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	
	post_to_delete = Posts.query.get_or_404(id)
	user_id = current_user.id
	if user_id == post_to_delete.poster_id:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()
			# return message
			flash("Blog Post Deleted Successfully!")
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)
		except:
			flash("There was a problem deleting.  Try again!")
			# logic error
			#return render_template("post.html", post=post_to_delete)
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)
	else:
		flash("You are not authorized to delete that post.  Try again!")	
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)



############## USERS #############

# create a Dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	record_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		record_to_update.name = request.form['name']
		record_to_update.username = request.form['username']
		record_to_update.email = request.form['email']
		record_to_update.favorite_color = request.form['favorite_color']
		record_to_update.about_author = request.form['about_author']

		# grab the filename of profile_pic image 
		record_to_update.profile_pic = request.files['profile_pic']
		pic_filename = secure_filename(record_to_update.profile_pic.filename)

		# set uuid
		pic_name = str(uuid.uuid1()) + "_" + pic_filename

		# save that image  !!! bug -- saves to correct folder. TBD : need to retrieve from same folder
		record_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

		# now save the pic_name to the actual db column
		record_to_update.profile_pic = pic_name

		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("dashboard.html", 
			form=form,
			record_to_update = record_to_update, id=id)

		except:
			flash("Error: There was a problem. Try it again!")
			return render_template("dashboard.html", 
			form=form,
			record_to_update = record_to_update,
			id=id)

	else:
		return render_template("dashboard.html", 
		form=form,
		record_to_update = record_to_update,
		id=id)
	
	return render_template("dashboard.html")



# create a Users model
# must inherit from UserMixin to implement flask user authentication
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    ## postgresql does not allow field length with Text column
    #- about_author = db.Column(db.Text(500), nullable=True)
    about_author = db.Column(db.Text(), nullable=True)
    profile_pic = db.Column(db.String(120), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # user can have many posts - (one to many)
    posts = db.relationship('Posts', backref='poster')
    
    # password-hash added + @property
    # @property is a built-in decorator that lets you define a method 
    # in a class that can be accessed like an attribute — 
    # without using parentheses.
    password_hash = db.Column(db.String(256), nullable=False)

    @property
    def password(self):
    	raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
    	self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
    	return check_password_hash(self.password_hash, password)

    # create a string representation
    def __repr__(self):
    	#return f"<Task id={self.id%r}, name={self.name%r}, email={self.email%r},favorite_color={self.favorite_color%r}>"
    	return '<Name %r>' % self.name

    # create a string representation
    def __repr__(self):
    	#return f"<title={self.title%r}, slug={self.slug%r}>"
    	return '<Title %r>' % self.title, '<Slug %r>' % self.slug

# localhost:5000/user/<name>
@app.route('/user/<string:name>')
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
			# generate password hash before save
			hashed_password = generate_password_hash(form.password_hash.data)
			user = Users(name=form.name.data, username=form.username.data,
			 	email = form.email.data,
				favorite_color = form.favorite_color.data,
				about_author = form.about_author.data,
				profile_pic = form.profile_pic .data,
				password_hash = hashed_password)
			db.session.add(user)
			db.session.commit()

		name = form.name.data
		
		# clear the form
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.favorite_color.data = ''
		password_hash = ''
		form.about_author.data = ''
		form.profile_pic = ''
		flash("User Added Successfully!")

	our_users = Users.query.order_by(Users.date_created)

	return render_template("add_user.html", name=name, 
		form=form, our_users=our_users)


# update a database record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	form = UserForm()
	record_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		record_to_update.name = request.form['name']
		record_to_update.username = request.form['username']
		record_to_update.email = request.form['email']
		record_to_update.favorite_color = request.form['favorite_color']
		record_to_update.about_author = request.form['about_author']
		record_to_update.profile_pic = request.form['profile_pic']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html", 
			form=form,
			record_to_update = record_to_update, id=id)

		except:
			flash("Error: There was a problem. Try it again!")
			return render_template("update.html", 
			form=form,
			record_to_update = record_to_update,
			id=id)

	else:
		return render_template("update.html", 
		form=form,
		record_to_update = record_to_update,
		id=id)

# delete a user record 
@app.route('/delete/<int:id>')
@login_required
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


############## PASSWORD #############


# create a password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	# declare variables - None for the first time display
	email = None # None for the first time display
	password = None
	pw_to_check_rec = None
	passed = None

	form = PasswordForm()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# clear the form
		form.email.data = ''
		form.password_hash.data = ''
		
		# look up user by email address
		pw_to_check_rec = Users.query.filter_by(email=email).first()
		
		# check hashed password
		passed = check_password_hash(pw_to_check_rec.password_hash, password)

	return render_template("test_pw.html", email=email, 
		password=password,
		pw_to_check_rec=pw_to_check_rec,
		passed = passed,
		form=form)


############## NAME #############

# create a name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None # None for the first time display
	form = NamerForm()
	if form.validate_on_submit():
		#same as: name = request.form['name'] ~~ name = form.name.data
		name = form.name.data
		# clear the form
		form.name.data = ''
		flash("Form Submitted Successfully!")

	return render_template("name.html", name=name, form=form)


############## HELLO WORLD ##########

# integrate db during startup
#
# @app.before_first_request
#def initialize_database():
#	db.create_all()
#

############## INDEX ##########

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



############## ADMIN ##############

# create admin page
@app.route('/admin')
@login_required
def admin():

	id = current_user.id 
	if id == 19:
		return render_template("admin.html") 
	else:
		flash("You Must Be Admin To Access Admin Page")
		return redirect(url_for('dashboard'))


############## ERRORS #############

# create custom error pages
# invalid url
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


# internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500



############## JSONIFY #############

# JSON - jsonify 
# this dictionary can be called from other website
# must import jsonify from flask
@app.route('/date')
def get_current_date():
	favorite_pizza = {
		"John": "Pepperoni",
		"Mary": "Cheese",
		"Tim": "Mushroom"
	}
	return favorite_pizza
	#return jsonify(favorite_pizza)
	#return { "Date":date.today() }

