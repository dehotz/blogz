from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] =  True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:zgolb@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'on6MoOy7k0NKGK0y7l3de6LIoNicy9'

class Blog(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(1000))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __init__(self, title, body, owner):
		self.title = title
		self.body = body
		self.owner = owner

class User(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20))
	password = db.Column(db.String(20))
	blogs = db.relationship('Blog', backref='owner')
	
	def __init__(self, username, password):
		self.username = username
		self.password = password

@app.before_request
def require_login():
	allowed_routes = ['login','signup','blog','index']
	if request.endpoint not in allowed_routes and 'username' not in session:
		return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
	blog_id = request.args.get("id")
	blog_user = request.args.get("user")

	if blog_id:
		blogs = Blog.query.filter_by(id=blog_id).all()
	elif blog_user:
		blogs = Blog.query.join(User).filter_by(username=blog_user).all()
		return render_template('singleuser.html', blogs=blogs)	
	else:
		blogs = Blog.query.join(User).all()
		
	return render_template('bloglist.html', blogs=blogs)	

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']

		flash_error = ""
		
		if title == '':
			flash_error = "Please fill in the title." ##refactor for flash messaging
		
		if body == '':
			flash_error = "Please fill in the body." ##refactor for flash messaging

		if not flash_error:
			new_entry = Blog(title, body, current_user())
			db.session.add(new_entry)
			db.session.commit()
			blog_id = new_entry.id
			blogs = Blog.query.filter_by(id=blog_id).all()
			return redirect('/blog?id='+str(blog_id))
		else:
			flash(flash_error, 'error')
			return render_template('newpost.html', title=title, body=body)

		return render_template('bloglist.html', blogs=blogs)
	
	return render_template('newpost.html')
	
@app.route('/', methods=['POST', 'GET'])
def index():
	users = User.query.all()

	return render_template('index.html', users=users)
	#return redirect('/blog')
	
def current_user():
	current_user = User.query.filter_by(username=session['username']).first()
	return current_user

@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user and user.password == password:
			session['username'] = username
			flash("Logged in")
			return redirect('/newpost')
		else:
			flash("User password incorrect or user does not exist", 'error')
			
	return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		verify = request.form['verify']
		
		flash_error = ""
		
		#validation password
		if password == '':
			flash_error = "Please enter a password."
		elif len(password) < 3:
			flash_error = "Password must be between 3 and 20 characters long."
		elif len(password) > 20:
			flash_error = "Password must be between 3 and 20 characters long."
		elif ' ' in password:
			flash_error = "Password must not contain spaces."
		elif password != verify:
			flash_error = "Passwords must match."
		
		#username validation
		if username == '':
			flash_error = "Please enter a username."
		elif len(username) < 3:
			flash_error = "Username must be between 3 and 20 characters long."
		elif len(username) > 20:
			flash_error = "Username must be between 3 and 20 characters long."
		elif ' ' in username:
			flash_error = "Username must not contain spaces."
		
		existing_user = User.query.filter_by(username=username).first()
		if existing_user:
			flash_error = "User with that name already exists."
		
		if not existing_user and not flash_error:
			new_user = User(username, password)
			db.session.add(new_user)
			db.session.commit()
			session['username'] = username
			flash("Logged in")
			return redirect('/')
		else:
			#todo - user better response messaging ##Probably do the flash error messaging also
			flash(flash_error, 'error')
			return redirect('/signup')		
		
	return render_template('signup.html')	

@app.route("/logout", methods=['POST'])
def logout():
	del session['username']
	return redirect("/blog")
	
if __name__ == '__main__':
	app.run()