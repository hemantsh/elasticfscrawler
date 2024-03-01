
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from elasticsearch import Elasticsearch 
import os, time 
import pycountry
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:RKKanika_SinghalBiz4_@127.0.0.1/elasticsearch27' 
es = Elasticsearch(host,basic_auth=(user,password),verify_certs=False)
db = SQLAlchemy(app)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    displayname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  
    is_admin = db.Column(db.Boolean, default=False)
    countries = db.Column(db.String(200), nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
class Search(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    search_query = db.Column(db.String(255), nullable=False)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id): 
   return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    create_user = request.args.get('create_user')
    
    if request.method == 'POST':
        email = request.form['email']
        displayname = request.form['displayname']
        password = request.form['password']
        countries = request.form['countries']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'error')
            return redirect(url_for('register'))

        if current_user.is_authenticated:
            current_user.email = email
            current_user.displayname = displayname
            current_user.set_password(password)
            current_user.countries = countries
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('login'))   
        
        new_user = User(email=email, displayname=displayname, countries=countries)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully with email: {}'.format(email), 'success')
        return redirect(url_for('login'))

    return render_template('register.html', create_user=create_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
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


@app.route('/search/results', methods=['POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form['input']
        email = current_user.email
        new_search = Search(email=email, search_query=search_query)
        db.session.add(new_search)
        db.session.commit()
        return render_template('results.html', input=search_query)
    return redirect(url_for('home'))


    # Perform Elasticsearch search
    # res = es.search(
    #     index=indexName,
    #     body={
    #         "query": {"match_phrase": {"content": {"query": search_query, "slop": 1}}},
    #         "size": 500,
    #         "highlight": {"pre_tags": ['<b>'], "post_tags": ["</b>"], "fields": {"content": {}}}
    #     })

    # # Process search results
    # for hit in res['hits']['hits']:
    #     hit['good_summary'] = '….'.join(hit['highlight']['content'][1:])
    #     hit['virtual'] = hit['_source']['path']['virtual']
    #     tokens = hit['_source']['path']['real'].split("/")
    #     hit['year'] = tokens[1]
    #     hit['case'] = tokens[2]
    #     hit['_source']['content'] = ""


@app.route('/home/')
@login_required
def home():
    return render_template('results.html')

 
 
@app.route('/admin/report', methods=['GET', 'POST'])
@login_required
def report():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        search_queries = Search.query.filter(Search.timestamp >= start_date, Search.timestamp <= end_date).all()
        search_results = []
        for query in search_queries:
            search_results.append({
                'timestamp': query.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'email': query.email,
                'search_query': query.search_query
            })
        return render_template('report.html', search_queries=search_results)
    else:
        return render_template('report.html', search_queries=[])

 
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables
    app.secret_key = 'supersecretkey'  # Secret key for flashing messages
    app.run('127.0.0.1', debug=True)