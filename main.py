from functools import reduce
import re
from flask import Flask, request, jsonify

from incomfort_constraints import check_constraint
from influxdb_service import init_influxdb, request_influxBD

app = Flask(__name__)

MEASURES_LIST = ['%', 'dBA', 'ppm', '°C', 'µg\/m³']
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
        if arg not in request.args:
            return error(f'Missing argument : {arg}')
    
    # Getting parameters
    tStart = int(request.args.get('start'))
    tEnd = int(request.args.get('end'))
    tInterval = (request.args.get('interval'))
    measures = parseArray(request.args.get('measures'))
    discomfort = parseArray(request.args.get('discomfort'))
    salle = request.args.get('salle') if request.args.get('salle') is not None else ""

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

    return filter_data(tStart, tEnd, tInterval, convert_regex(measures), discomfort, salle)

if __name__ == '__main__':
    app.run(debug=True)
def filter_data(tStart, tEnd, tInterval, measures, incomfort, salle):
    init_influxdb()
    request = f'''
    import "strings"
    import "regexp"
    
    from(bucket: "IUT_BUCKET")
          |> range(start: {tStart}, stop: {tEnd})
          |> filter(fn: (r) => r["_measurement"] =~ {measures})
          |> filter(fn: (r) => r["_field"] == "value")
          |> filter(fn: (r) => r["domain"] == "sensor")
          |> filter(fn: (r) => strings.hasPrefix(v: r["entity_id"], prefix: "{salle}"))
          |> aggregateWindow(every: {tInterval}, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
    data = request_influxBD(request)
    data_after_constraints = check_constraint(data, incomfort)
    return data_after_constraints

def convert_regex(table):
    return "/" + reduce(lambda acc, val: f'{acc}|{val}', map(str, table)) + "/"

def regex_match(input_string, regex_pattern):
    return re.match(regex_pattern, input_string)
