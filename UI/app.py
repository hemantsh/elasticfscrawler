from flask import Flask, render_template, request, flash, redirect, url_for, session
from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pycountry

from dotenv  import load_dotenv
from pathlib import Path


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

os.chdir(dir)


app = Flask(__name__)
es = Elasticsearch(host,basic_auth=(user,password),verify_certs=False)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:RKKanika_SinghalBiz4_@127.0.0.1/elasticsearch7'
# db.init_app(app)

# es = Elasticsearch(f'https://{user}:{password}@localhost:9200',verify_certs=False)
 

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['userName']
        countries = request.form['countries']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        new_user = User(first_name=first_name, last_name=last_name, countries=countries, username=username)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    countries = [country.name for country in pycountry.countries]
    return render_template('register.html', countries=countries)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['userName'] 

        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Login successful!', 'success')
            session['username'] = username  # Store UserName in session
            return redirect(url_for('home'))
        else:
            flash('Invalid username. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/search/results', methods=['POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['input']
        user_id = request.form['userId']
        if user_id:

            # Store search in Search table

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


        return render_template('results.html', res=res, input=search_query, user_id=user_id)  # Pass user_id to template


@app.route('/home')
def home():
    return render_template('results.html')


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'  # Secret key for flashing messages
    with app.app_context():
        db.create_all()  # Create all database tables
    app.run('127.0.0.1', debug=True)






 

 