from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import os

os.chdir('/Users/hemant/projects/FSElastic/git/UI')
password = os.getenv('ELASTIC_PASSWORD')
app = Flask(__name__)
es = Elasticsearch('https://localhost:9200',basic_auth=("user","pass"),verify_certs=False)
# es = Elasticsearch('https://user:pass@localhost:9200',verify_certs=False)


@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search/results', methods=['GET','POST'])
def request_search():
    search_term = request.form['input']
    res = es.search(
    index='idx',
    body={
    "query" : { "match_phrase": {"content": {"query": search_term, "slop": 1 } }},
    "highlight" : {"pre_tags" : ['<b>'] , "post_tags" : ["</b>"], "fields" : {"content":{}}}})
    # res['ST']=search_term

    for hit in res['hits']['hits']:
        hit['good_summary']='….'.join(hit['highlight']['content'][1:])
        hit['virtual'] = hit['_source']['path']['virtual']
        tokens = hit['virtual'].split("/")
        # hit['year'] = tokens[1]
        # hit['case'] = tokens[2]

        #local test
        tokens = hit['_source']['path']['real'].split("/")
        hit['year'] = tokens[1]
        hit['case'] = tokens[2]
        
    return render_template('results.html', res=res)
                        
if __name__ == '__main__':
    app.run('127.0.0.1', debug=True)
