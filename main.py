from flask import Flask
from flask import request

from data_types import DataTypes

app = Flask(__name__)

@app.route('/data')
def data():
    tStart = request.args.get('start')
    tEnd = request.args.get('end')
    tInterval = request.args.get('interval')
    mesures = request.args.get('mesures')
    incomfort = request.args.get('incomfort')
    parsed_mesures = parseArray(mesures)
    parsed_incomfort = parseArray(incomfort)
    return f"Mesure filters: {parsed_mesures},\n Incomfort filters: {parsed_incomfort} TimTimestamp start: {tStart},\n Timestamp end: {tEnd}, Intervale: {tInterval} minutes"

def parseArray(array):
    parsed_array = array.split(',')
    parsed_array = [value for value in parsed_array]
    return parsed_array