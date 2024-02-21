from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from elasticsearch import Elasticsearch 
import os
import pycountry
from flask_bcrypt import Bcrypt

from dotenv  import load_dotenv
from flask_login import current_user
from pathlib import Path
bcrypt = Bcrypt()

dotenv_path = Path('../.env')
User = Path('../sql_db/create_table')
Search = Path('../sql_db/create_table')
db = Path('../sql_db/create_table')
load_dotenv(dotenv_path=dotenv_path)


dir = os.getenv('FLASK_APP_DIR')
user = os.getenv('ELASTIC_USER')
password = os.getenv('ELASTIC_PASSWORD')
host = os.getenv('ELASTIC_HOST')
indexName = os.getenv('INDEX_NAME')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:RKKanika_SinghalBiz4_@127.0.0.1/elasticsearch21' 
es = Elasticsearch(host,basic_auth=(user,password),verify_certs=False)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    displayname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Storing the encrypted password
    is_admin = db.Column(db.Boolean, default=False)
    countries = db.Column(db.String(200), nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# Define Search model
class Search(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    search_query = db.Column(db.String(255))

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('register'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        displayname = request.form['displayname']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('register'))
        
        new_user = User(email=email, displayname=displayname)
        new_user.set_password(password)  
        db.session.add(new_user)
        db.session.commit()

        if current_user.is_authenticated:
            # User is logged in
            user_email = current_user.email
            print(f"User with email '{user_email}' is logged in.")
        else:
            # User is not logged in
            print("No user is logged in.")

        flash(f'User registered successfully with email: {email}')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search/results', methods=['POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['input']
        user_id = request.form['userId']
        if user_id:
            new_search = Search(user_id=user_id, search_query=search_query)
            db.session.add(new_search)
            db.session.commit()
        return redirect(url_for('home'))

    if not user_name:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

    new_search = Search(user_name=user_name, search_query=search_query)
    db.session.add(new_search)
    db.session.commit()

    return render_template('results.html', res=res, input=search_query, user_id=user_id)  

@app.route('/home/')
def home():
    return render_template('results.html')
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables
    app.secret_key = 'supersecretkey'  # Secret key for flashing messages
    app.run('127.0.0.1', debug=True)
