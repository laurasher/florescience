from flask import Flask, render_template, jsonify,\
	request, json, send_from_directory
import os
from flask_pymongo import PyMongo
from arxiv_etl import *
import json

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/arxiv"
db = PyMongo(app).db

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/queryOne', methods=['GET'])
def queryOne():
    sample = db.records.find({})
    cursor = getCursor(sample)
    # cursor is a json array with the contents of the query
    debug_print(cursor[0], "first element of cursor")
    return cursor[0]

@app.route('/queryField', methods=['GET', 'POST'])
def queryField():
    r = request.get_json()
    query_str = r['q']
    sample = db.records.find({"subject": {"$regex": f".*{query_str}.*"}})
    cursor = getCursor(sample)
    cursor_json = json.dumps(cursor)
    # debug_print(cursor_json, "cursor_json")
    return cursor_json

@app.route('/queryAll', methods=['GET'])
def queryAll():
    sample = db.records.find({})
    json_res = getCursor(sample)
    cursor_json = json.dumps(json_res)
    return cursor_json

@app.route('/getTs', methods=['GET'])
def getTs():
    sample = db.records.find({})
    json_res = getCursor(sample)
    ts_json = getTimeseries(json_res)
    return ts_json



if __name__ == '__main__':
    app.run(debug=True)
