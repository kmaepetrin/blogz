from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggin@localhost:8890/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'bootpootddd'

#databases

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.String(1000000))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, text, owner, pub_date=None):
        self.name = name
        self.text = text
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#posting

@app.route('/newpost', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        name = request.form['blog-name']
        text = request.form['blog-text']
        owner = User.query.filter_by(username=session['username']).first()
        
        if len(name) > 0 and len(text) >0:
            flash("Blog added!")
            new_blog = Blog(name, text, owner)
            db.session.add(new_blog)
            db.session.commit()

            str_id = str(new_blog.id)

            return redirect('/blog?id=' + str_id)

        if len(name) == 0:
            flash("Please input a title!", "error")
        if len(text) == 0:
            flash("Please fill in the blog text!", "error")

    return render_template('newpost.html')

#viewing

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    blog_id = request.args.get('id')
    blogs = Blog.query.all()
    user_id = request.args.get('user')
    users = User.query.all()

    if request.args:
        blog = Blog.query.filter_by(id=blog_id).first()
        user = User.query.filter_by(id=user_id).first()

        return render_template('blog.html', blog=blog, user=user)
    else:
        user = User.query.filter_by(id=user_id).first()

        return render_template('bloglist.html', blogs=blogs, user=user, users=users)

@app.route('/', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get('id')
    blogs = Blog.query.all()
    user_id = request.args.get('user')
    users = User.query.all()

    if request.args:
        user = User.query.filter_by(id=user_id).first()
        blogs = Blog.query.filter_by(owner_id=user_id).all()

        return render_template('user.html', user=user, blogs=blogs)
    else:
        user = User.query.filter_by(id=user_id).first()
        users = User.query.all()

        return render_template('index.html', users=users, user=user)

# login, out, etc

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
        elif not user:
            flash("User does not exist", "error")
        elif user.password != password:
            flash("User password is incorrect", "error")
        
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('login')

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash("User already exists", "error")
            return redirect('/signup')
        elif username == "":
            flash("Please input a username!", "error")
            return redirect('/signup')
        elif len(username) < 3:
            flash("Your username is too short", "error")
            return redirect('/signup')
        elif len(password) < 3:
            flash("Your password is too short", "error")
            return redirect('/signup')
        elif password == "":
            flash("Please input a password!", "error")
            return redirect('/signup')
        elif verify == "":
            flash("Please verify your password!", "error")
            return redirect('/signup')
        elif verify != password:
            flash("Your passwords do not match!", "error")
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/newpost')
    
    return render_template('signup.html')

            
if __name__ == '__main__':
    app.run()