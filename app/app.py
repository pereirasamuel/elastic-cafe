from datetime import datetime
from flask import Flask, jsonify, request, make_response, render_template
from elasticsearch import Elasticsearch
import os 
from dotenv import load_dotenv
from elasticapm.contrib.flask import ElasticAPM
from flask_pymongo import PyMongo
from bson import json_util, ObjectId
import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
from pygments.formatters import HtmlFormatter



load_dotenv()

app = Flask(__name__)

ES_PWD = os.getenv("ES_PWD") 
ES_IP = os.getenv("ES_IP")

app.config['ES_PWD'] = os.getenv('ES_PWD')
app.config['ES_IP'] = os.getenv('ES_IP')

es = Elasticsearch(
    "https://{0}:9200".format(ES_IP),
    basic_auth=("sysadmin", ES_PWD),
    verify_certs=False
)

app.config['ELASTIC_APM'] = {
  'SERVICE_NAME': 'flaskApp',
  'SERVER_URL': 'http://{0}:8200'.format(ES_IP),
  'ENVIRONMENT': 'production',
}

app.config["MONGO_URI"] = 'mongodb://' + os.getenv('MONGODB_USERNAME') + ':' + os.getenv('MONGODB_PASSWORD') + '@' + os.getenv('MONGODB_HOSTNAME') + ':27017/' + os.getenv('MONGODB_DATABASE') + '?authSource=admin'
mongo = PyMongo(app)
db = mongo.db

apm = ElasticAPM(app)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api():
    return render_template('api.html')

@app.route('/coffee/all', methods=['GET'])
def index():
    coffees = db.coffee.find()
    results = es.search(
        index='elasticcafe-app',
        query={"match_all":{}},
        filter_path=["hits.hits._source.coffee","hits.hits._source.price","hits.hits._source.sugar","hits.hits._source.customer"]
        )

    db_results = json_util.dumps([coffee for coffee in coffees])

    return jsonify(results['hits']['hits'])


@app.route('/add_coffee', methods=['POST'])
def add_coffee():
    request_data = request.get_json()
    coffee = request_data['coffee']
    price = request_data['price']
    sugar = request_data['sugar']
    customer = request_data['customer']

    doc = {
        'coffee': coffee,
        'price': price,
        'sugar': sugar,
        'customer': customer,
        'timestamp': datetime.now()
    }
    
    response = es.index(index='elasticcafe-app', document=doc)
    db.coffee.insert_one(doc)

    return jsonify(response['result']),201

@app.route('/search_customer/<customer>', methods=['POST'])
def search_customer(customer):

    body = {
        "query": {
            "match": {
                "customer": customer
            }
        }
    }

    res = es.search(
            index="elasticcafe-app", 
            body=body,
            filter_path=["hits.hits._source.coffee","hits.hits._source.price","hits.hits._source.sugar","hits.hits._source.customer"]
            )

    return jsonify(res['hits']['hits'])



@app.route('/search_coffee/<coffee>', methods=['POST'])
def search_coffee(coffee):

    body = {
        "query": {
            "match": {
                "coffee": coffee
            }
        }
    }

    res = es.search(
            index="elasticcafe-app", 
            body=body, 
            filter_path=["hits.hits._source.coffee","hits.hits._source.price","hits.hits._source.sugar","hits.hits._source.customer"]
            )

    return jsonify(res['hits']['hits'])

