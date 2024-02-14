from flask import Flask, render_template, request, flash, redirect, url_for
from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pycountry
import hashlib

from dotenv  import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

dir = os.getenv('FLASK_APP_DIR')
user = os.getenv('ELASTIC_USER')
password = os.getenv('ELASTIC_PASSWORD')
host = os.getenv('ELASTIC_HOST')
indexName = os.getenv('INDEX_NAME')

os.chdir(dir)

app = Flask(__name__)
es = Elasticsearch(host,basic_auth=(user,password),verify_certs=False)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:RKKanika_SinghalBiz4_@127.0.0.1/elasticsearch'
db = SQLAlchemy(app)
# es = Elasticsearch(f'https://{user}:{password}@localhost:9200',verify_certs=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    countries = db.Column(db.String(255))

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    search_query = db.Column(db.String(255))


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        countries = request.form['countries']

        new_user = User(first_name=first_name, last_name=last_name, countries=countries)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    countries = [country.name for country in pycountry.countries]
    return render_template('register.html', countries=countries)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['userId']
        if user_id:
            # Store userId in Search table
            new_search = Search(user_id=user_id, search_query="Logged in")
            db.session.add(new_search)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('login.html')



@app.route('/search/results', methods=['GET','POST'])
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

        # Perform Elasticsearch search
        res = es.search(
            index=indexName,
            body={
                "query": {"match_phrase": {"content": {"query": search_query, "slop": 1}}},
                "size": 500,
                "highlight": {"pre_tags": ['<b>'], "post_tags": ["</b>"], "fields": {"content": {}}}
            })

        # Process search results
        for hit in res['hits']['hits']:
            hit['good_summary'] = '….'.join(hit['highlight']['content'][1:])
            hit['virtual'] = hit['_source']['path']['virtual']
            tokens = hit['_source']['path']['real'].split("/")
            hit['year'] = tokens[1]
            hit['case'] = tokens[2]
            hit['_source']['content'] = ""

        return render_template('results.html', res=res, input=search_query)


@app.route('/home')
def home():
    return render_template('results.html')


if __name__ == '__main__':
    app.secret_key = 'supersecretkey'  # Secret key for flashing messages
    with app.app_context():
        db.create_all()  # Create all database tables
    app.run('127.0.0.1', debug=True)

