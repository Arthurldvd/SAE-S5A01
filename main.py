from functools import reduce

from flask import Flask, request, jsonify
import re

from incomfort_constraints import check_constraint
from influxdb_service import init_influxdb, request_influxBD

app = Flask(__name__)

MESURES_LIST = ['%', 'dBA', 'ppm', '°C', 'µg\/m³']
DISCOMFORT_LIST = ['co2', 'humidity', 'uv', 'db', 'temperature']

def parseArray(array):
    return array.split(',')

def error(message: str):
    return {
        'error' : message
    }

def addition(x, y):
    for i in range(y):
        x = x + 1

@app.route('/data')
def data():
    required_args = ['start', 'end', 'interval']
    for arg in required_args:
        if arg not in request.args:
            return error(f'Missing argument : {arg}')
    
    # Getting parameters
    tStart = int(request.args.get('start'))
    tEnd = int(request.args.get('end'))
    tInterval = (request.args.get('interval'))
    mesures = parseArray(request.args.get('mesures')) if request.args.get('salle') is not None else MESURES_LIST
    discomfort = parseArray(request.args.get('discomfort')) if request.args.get('discomfort') is not None else DISCOMFORT_LIST
    salle = request.args.get('salle') if request.args.get('salle') is not None else ""

    # Verification
    for m in mesures:
        if (m not in MESURES_LIST):
            return error(f"'{m}' is not a known mesure.")

    for m in discomfort:
        if (m not in DISCOMFORT_LIST):
            return error(f"'{m}' is not a known discomfort.")

    if (tStart < 0): return error("Start timestamp can't be negative")
    if (tEnd < 0): return error("End timestamp can't be negative")
    if (tStart > tEnd): return error("Start timestamp can't be superior to end timestamp")
    if not (regex_match(str(tInterval), r'^[1-9]+\d*(m|h|d|w|mo|y])$')): return error("Interval is not in a correct format")

    return filter_data(tStart, tEnd, tInterval, convert_regex(mesures), discomfort, salle)

if __name__ == '__main__':
    app.run(debug=True)
def filter_data(tStart, tEnd, tInterval, mesures, incomfort, salle):
    init_influxdb()
    request = f'''
    import "strings"
    import "regexp"
    
    from(bucket: "IUT_BUCKET")
          |> range(start: {tStart}, stop: {tEnd})
          |> filter(fn: (r) => r["_measurement"] =~ {mesures})
          |> filter(fn: (r) => r["_field"] == "value")
          |> filter(fn: (r) => r["domain"] == "sensor")
          |> filter(fn: (r) => strings.hasPrefix(v: r["entity_id"], prefix: "{salle}"))
          |> aggregateWindow(every: {tInterval}, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
    print(request)
    data = request_influxBD(request)
    data_after_constraints = check_constraint(data, incomfort)
    return data_after_constraints

def convert_regex(table):
    return "/" + reduce(lambda acc, val: f'{acc}|{val}', map(str, table)) + "/"

def regex_match(input_string, regex_pattern):
    return re.match(regex_pattern, input_string)
