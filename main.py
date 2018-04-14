from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] =  True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:golbadliub@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'on6MoOy7k0NKGK0y7l3d'

class Blog(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(1000))	
	
	def __init__(self, title, body):
		self.title = title
		self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog():
	blog_id = request.args.get("id")
	
	if blog_id:
		blogs = Blog.query.filter_by(id=blog_id).all()
	else:
		blogs = Blog.query.all()
		
	return render_template('bloglist.html', blogs=blogs)	

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']

		title_error = ""
		body_error = ""
		
		if title == '':
			title_error = "Please fill in the title."
		
		if body == '':
			body_error = "Please fill in the body."

		if not title_error and not body_error:
			new_entry = Blog(title, body)
			db.session.add(new_entry)
			db.session.commit()
			blog_id = new_entry.id
			blogs = Blog.query.filter_by(id=blog_id).all()
		else:
			return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)

		return render_template('bloglist.html', blogs=blogs)
	
	return render_template('newpost.html')
	
@app.route('/', methods=['POST', 'GET'])
def index():

	return redirect('/blog')

if __name__ == '__main__':
	app.run()