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
from werkzeug.security import generate_password_hash

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
db = SQLAlchemy(app)




# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    displayname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Storing the encrypted password
    is_admin = db.Column(db.Boolean, default=True)
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


# @login_manager.user_loader
# def load_user(email):
#     return User.query.filter_by(email=email).first()


@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        displayname = request.form['displayname']
        password = request.form['password']
        countries = request.form['countries']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.')
            return redirect(url_for('register'))

        if current_user.is_authenticated:
            # User is logged in, update profile
            current_user.email = email
            current_user.displayname = displayname
            current_user.set_password(password)
            current_user.countries = countries
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to login after profile update
        

        # User is not logged in, create new user
        new_user = User(email=email, displayname=displayname, countries=countries)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully with email: {}'.format(email), 'success')
        return redirect(url_for('login'))

    # # GET request
    # if current_user.is_authenticated:
    #     # User is logged in, pre-fill form fields
    #     email = current_user.email
    #     displayname = current_user.displayname
    #     countries = current_user.countries
    #     return render_template('register.html')
    # else:
    #     # User is not logged in, render registration form
    #     return render_template('register.html')
    
    
    #     # GET request
    # title = 'Registration'
    # if current_user.is_authenticated:
    #     title = 'My Profile'

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_home'))  # Redirect to admin homepage if user is admin
            else:
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
    return redirect(url_for('login'))


# @app.route('/search/results', methods=['POST'])
# @login_required
# def search():
#     if request.method == 'POST':
#         search_query = request.form['input']
#         user_id = request.form['userId']
#         if user_id:
#             new_search = Search(user_id=user_id, search_query=search_query)
#             db.session.add(new_search)
#             db.session.commit()
#         return redirect(url_for('home'))

#     if not user_name:
#         flash('You need to login first.', 'danger')
#         return redirect(url_for('login'))

#     new_search = Search(user_name=user_name, search_query=search_query)
#     db.session.add(new_search)
#     db.session.commit()

#     return render_template('results.html', res=res, input=search_query, user_id=user_id)  


@app.route('/search/results', methods=['POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form['input']
        email = current_user.email
        new_search = Search(email=email, search_query=search_query)
        db.session.add(new_search)
        db.session.commit()
        
        # Retrieve the selected start and end dates from the form
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        
        # Query the database for search queries between the selected dates
        search_queries = Search.query.filter(Search.timestamp.between(start_date, end_date)).all()
        
        # Log the search queries to the console
        for query in search_queries:
            print("Search Query:", query.search_query)
        
        # Render the results template with the search query
        return render_template('results.html', input=search_query)


@app.route('/home/')
@login_required
def home():
    return render_template('results.html')


@app.route('/admin/home')
@login_required
def admin_home():
    if not current_user.is_admin:
        flash('Access denied. You are not an admin.', 'danger')
        return redirect(url_for('home'))
    return render_template('admin_home.html')


@app.route('/admin/report')
def report():
    return render_template('generate_report.html')
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables
    app.secret_key = 'supersecretkey'  # Secret key for flashing messages
    app.run('127.0.0.1', debug=True)

