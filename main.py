import re
from functools import reduce

from flask import Flask, request, jsonify

from ia_prediction import predict_temperature
from incomfort_constraints import modify_object
from influxdb_service import filter_data

app = Flask(__name__)

MEASURES_LIST = ['%', 'dBA', 'ppm', '°C', 'µg/m³', 'lx',
                 "binary_sensor.d251_1_co2_highly_polluted",
                 "binary_sensor.d251_1_co2_moderately_polluted",
                 "binary_sensor.d251_1_co2_slightly_polluted",
                 "binary_sensor.d251_1_multisensor_motion_detection",
                 "binary_sensor.d351_1_co2_highly_polluted",
                 "binary_sensor.d351_1_co2_moderately_polluted",
                 "binary_sensor.d351_1_co2_slightly_polluted",
                 "binary_sensor.d351_1_multisensor_motion_detection",
                 "binary_sensor.d351_2_co2_highly_polluted",
                 "binary_sensor.d351_2_co2_moderately_polluted",
                 "binary_sensor.d351_2_co2_slightly_polluted",
                 "binary_sensor.d351_2_multisensor_motion_detection",
                 "binary_sensor.d360_1_co2_highly_polluted"
                 "binary_sensor.d360_1_co2_moderately_polluted"
                 "binary_sensor.d360_1_co2_slightly_polluted"
                 "binary_sensor.d360_1_co2_multisensor_motion_detection"]

DISCOMFORT_LIST = ['co2', 'humidity', 'uv', 'db', 'temperature']

OUTPUT_TYPE = ['mean', 'median', 'last']

BUCKET_LIST = ['IUT_BUCKET', 'POCHATSA_BUCKET']


def parseArray(array):
    if array is None: return None
    return [value for value in array.split(',')]


def error(message: str):
    return jsonify({
        'error': message
    }), 400


def group_by_time(filtered_data, harmonizeData):
    distinct_times = set(entry._time for entry in filtered_data)

    if harmonizeData:
        for time in distinct_times:
            data_field = [x for x in filtered_data if x._time == time]

        return data_field

    for time in distinct_times:
        data_field = [x for x in filtered_data if x._time == time]

    return data_field


@app.route('/data')
def data():
    required_args = ['bucket', 'start', 'end', 'interval']
    for arg in required_args:
        if arg not in request.json:
            return error(f'Missing argument : {arg}')

    # Getting parameters
    bucket = parseArray(request.json.get('bucket'))
    tStart = int(request.json.get('start'))
    tEnd = int(request.json.get('end'))
    tInterval = (request.json.get('interval'))
    measures = parseArray(request.json.get('measures'))
    discomfort = parseArray(request.json.get('discomfort'))
    output = parseArray(request.json.get('output'))
    salle = request.json.get('salle') if request.json.get('salle') is not None else ""
    supressError = request.json.get('supressError') if request.json.get('supressError') is not None else False
    harmonizeData = request.json.get('harmonizeData') if request.json.get('harmonizeData') is not None else True

    # Verification
    if not isinstance(harmonizeData, bool):
        return error("harmonizeData should be a boolean")

    bucket = BUCKET_LIST[0] if bucket is None else [m for m in bucket if m in BUCKET_LIST][0] or error(
        f"Unknown measure(s): {', '.join(set(bucket) - set(BUCKET_LIST))}")

    measures = MEASURES_LIST if measures is None else [m for m in measures if m in MEASURES_LIST] or error(
        f"Unknown measure(s): {', '.join(set(measures) - set(MEASURES_LIST))}")

    discomfort = DISCOMFORT_LIST if discomfort is None else [m for m in discomfort if m in DISCOMFORT_LIST] or error(
        f"Unknown discomfort(s): {', '.join(set(discomfort) - set(DISCOMFORT_LIST))}")

    output = 'mean' if output is None else [m for m in output if m in OUTPUT_TYPE][0] or error(
        f"Unknown output or several outputs : can only get one: {output}")

    if tStart < 0: return error("Start timestamp can't be negative.")
    if tEnd < 0: return error("End timestamp can't be negative.")
    if tStart > tEnd: return error("Start timestamp can't be superior to end timestamp.")
    if not (regex_match(str(tInterval), r'^[1-9]+\d*(m|h|d|w|mo|y])$')): return error(
        "Interval is not in a correct format.")

    filtered_data = filter_data(bucket, tStart, tEnd, tInterval, measures, salle, output)

    # filtered_data = group_by_time(filtered_data, harmonizeData)
    return modify_object(filtered_data, discomfort, harmonizeData, supressError)


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
    output = parseArray(request.json.get('output'))

    # Getting parameters (OPTIONNALS)
    tStart = int(request.json.get('start')) if not None else "1700703993"
    tEnd = int(request.json.get('end')) if not None else "1703172412"
    tInterval = (request.json.get('interval')) if not None else "1h"

    # Verification
    measures = MEASURES_LIST if measures is None else [m for m in measures if m in MEASURES_LIST] or error(
        f"Unknown measure(s): {', '.join(set(measures) - set(MEASURES_LIST))}")

    output = 'mean' if output is None else [m for m in output if m in OUTPUT_TYPE] or error(
        f"Unknown discomfort(s): {', '.join(set(output) - set(OUTPUT_TYPE))}")

    if tStart < 0: return error("Start timestamp can't be negative.")
    if tEnd < 0: return error("End timestamp can't be negative.")
    if tStart > tEnd: return error("Start timestamp can't be superior to end timestamp.")
    if not (regex_match(str(tInterval), r'^[1-9]+\d*(m|h|d|w|mo|y])$')): return error(
        "Interval is not in a correct format.")

    filtered_data = predict_temperature(tStart, tEnd, tInterval, measures, salle, prediction_hour)
    return str(filtered_data[0][0])


if __name__ == '__main__':
    app.run(debug=True)


def regex_match(input_string, regex_pattern):
    return re.match(regex_pattern, input_string)
