from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import os

os.chdir('/srv')
password = os.getenv('ELASTIC_PASSWORD',"W3lcomeAA**")
app = Flask(__name__)
es = Elasticsearch('https://localhost:9200',basic_auth=("elastic",password),verify_certs=False)
#es = Elasticsearch(f'https://elastic:{password}@localhost:9200',verify_certs=False)


@app.route('/')
def home():
    return render_template('results.html')

@app.route('/search/results', methods=['GET','POST'])
def request_search():
    
    search_term = request.form['input']
    res = es.search(
    index='idx',
    body={
    "query" : { "match_phrase": {"content": {"query": search_term, "slop": 1 } }},
    "size" : 500,
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
        hit['_source']['content'] = ""
        
    return render_template('results.html', res=res, input=search_term)
                        
if __name__ == '__main__':
    app.run('127.0.0.1', debug=True)
