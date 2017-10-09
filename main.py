from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog-a-build@localhost:8890/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.String(1000000))

    def __init__(self, name, text):
        self.name = name
        self.text = text

@app.route('/newpost', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        name = request.form['blog-name']
        text = request.form['blog-text']
        if len(name) > 0 and len(text) >0:
            flash("Blog added!")
            return redirect('/blog')
        else:
            flash("Please input a title and blog text!")

    return render_template('newpost.html')

@app.route('/added', methods=['POST'])
def added():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        name = request.form['blog-name']
        text = request.form['blog-text']
        new_blog = Blog(name, text)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()

    return render_template('index.html', blogs=blogs)

if __name__ == '__main__':
    app.run()