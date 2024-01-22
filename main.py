import re
from functools import reduce

from flask import Flask, request, jsonify

from ia_prediction import predict_temperature
from incomfort_constraints import check_constraint
from influxdb_service import filter_data

app = Flask(__name__)

MEASURES_LIST = ['%', 'dBA', 'ppm', '°C', 'µg/m³']
DISCOMFORT_LIST = ['co2', 'humidity', 'uv', 'db', 'temperature']

def parseArray(array):
    if array is None: return None
    return [value for value in array.split(',')]

def error(message: str):
    return jsonify({
        'error': message
    }), 400

@app.route('/data')
def data():
    required_args = ['start', 'end', 'interval']
    for arg in required_args:
        if arg not in request.json:
            return error(f'Missing argument : {arg}')
    
    # Getting parameters
    tStart = int(request.json.get('start'))
    tEnd = int(request.json.get('end'))
    tInterval = (request.json.get('interval'))
    measures = parseArray(request.json.get('measures'))
    print(measures)
    discomfort = parseArray(request.json.get('discomfort'))
    salle = request.json.get('salle') if request.json.get('salle') is not None else ""

    # Verification
    if (measures is None): measures = MEASURES_LIST
    else:
        for m in measures:
            if (m not in MEASURES_LIST):
                return error(f"'{m}' is not a known measure.")

    if (discomfort is None): discomfort = DISCOMFORT_LIST
    else:
        for m in discomfort:
            if (m not in DISCOMFORT_LIST):
                return error(f"'{m}' is not a known discomfort.")

    if (tStart < 0): return error("Start timestamp can't be negative.")
    if (tEnd < 0): return error("End timestamp can't be negative.")
    if (tStart > tEnd): return error("Start timestamp can't be superior to end timestamp.")
    if not (regex_match(str(tInterval), r'^[1-9]+\d*(m|h|d|w|mo|y])$')): return error("Interval is not in a correct format.")

    filtered_data = filter_data(tStart, tEnd, tInterval, measures, salle)
    return check_constraint(filtered_data, discomfort)


@app.route('/ia_prediction')
def ia_prediction():
    required_args = ['measures', 'salle', 'prediction_hour']
    for arg in required_args:
        if arg not in request.json:
            return error(f'Missing argument : {arg}')

    # Getting parameters (REQUIRED)
    measures = parseArray(request.json.get('measures'))
    salle = request.json.get('salle')
    prediction_hour = request.json.get('prediction_hour')

    # Getting parameters (OPTIONNALS)
    tStart = int(request.json.get('start')) if not None else "1700703993"
    tEnd = int(request.json.get('end')) if not None else "1703172412"
    tInterval = (request.json.get('interval')) if not None else "1h"

    # Verification
    if (measures is None):
        measures = MEASURES_LIST
    else:
        for m in measures:
            if (m not in MEASURES_LIST):
                return error(f"'{m}' is not a known measure.")

    if (tStart < 0): return error("Start timestamp can't be negative.")
    if (tEnd < 0): return error("End timestamp can't be negative.")
    if (tStart > tEnd): return error("Start timestamp can't be superior to end timestamp.")
    if not (regex_match(str(tInterval), r'^[1-9]+\d*(m|h|d|w|mo|y])$')): return error(
        "Interval is not in a correct format.")

    filtered_data = predict_temperature(tStart, tEnd, tInterval, measures, salle, prediction_hour)
    print(filtered_data)
    return filtered_data

if __name__ == '__main__':
    app.run(debug=True)

def regex_match(input_string, regex_pattern):
    return re.match(regex_pattern, input_string)



