import re
from functools import reduce

from flask import Flask, request, jsonify

from complexDictCreator import create_custom_object
from ia_prediction import predict_temperature
from incomfort_constraints import modify_object
from influxdb_service import filter_data
from window_detection import window_detection

app = Flask(__name__)

MEASURES_LIST = ["Humidité", "Fumée", "Décibels", "Luminosité", "Co2", "Co2 Volatile", "Température", "co2 Dew",
                 "Particules", "Ultra violets", "binary_sensor.d251_1_co2_highly_polluted",
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


def group_bytime(filtered_data, harmonizeData):
    distincttimes = set(entry.time for entry in filtered_data)

    if harmonizeData:
        for time in distincttimes:
            data_field = [x for x in filtered_data if x.time == time]

        return data_field

    for time in distincttimes:
        data_field = [x for x in filtered_data if x.time == time]

    return data_field

from flask import Flask, request
import re

app = Flask(__name__)

@app.route('/data')
def data():
    required_args = ['bucket', 'start', 'end', 'interval']
    for arg in required_args:
        if arg not in request.args:
            return error(f'Missing argument: {arg}')

    # Getting parameters
    bucket = parseArray(request.args.get('bucket'))
    tStart = int(request.args.get('start'))
    tEnd = int(request.args.get('end'))
    tInterval = request.args.get('interval')
    measures = parseArray(request.args.get('measures'))
    discomfort = parseArray(request.args.get('discomfort'))
    output = parseArray(request.args.get('output'))
    salle = request.args.get('salle', "")
    supressError = request.args.get('supress_errors', False, type=bool)
    harmonizeData = request.args.get('harmonize_data', True, type=bool)

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
        f"Unknown output or several outputs: can only get one: {output}")

    if tStart < 0: return error("Start timestamp can't be negative.")
    if tEnd < 0: return error("End timestamp can't be negative.")
    if tStart > tEnd: return error("Start timestamp can't be superior to end timestamp.")
    if not (re.match(r'^[1-9]+\d*(m|h|d|w|mo|y)$', str(tInterval))): return error(
        "Interval is not in a correct format.")

    filtered_data = filter_data(bucket, tStart, tEnd, tInterval, measures, salle, output)
    return create_custom_object(filtered_data,
        '''
        data::object#
            $time::list#
                $salle::list#
                    $mesure::list#
                        $inconforts
                        $entity_id
                        $mesure
                        $_value
                        ::classAttributes#
        ''')


@app.route('/ia_prediction')
def ia_prediction():
    required_args = ['measures', 'salle', 'prediction_hour']
    for arg in required_args:
        if arg not in request.args:
            return error(f'Missing argument: {arg}')

    # Getting parameters (REQUIRED)
    measures = parseArray(request.args.get('measures'))
    salle = request.args.get('salle')
    prediction_hour = request.args.get('prediction_hour')
    output = parseArray(request.args.get('output'))

    # Getting parameters (OPTIONNALS)
    tStart = int(request.args.get('start', "1700703993"))
    tEnd = int(request.args.get('end', "1703172412"))
    tInterval = request.args.get('interval', "1h")

    # Verification
    measures = MEASURES_LIST if measures is None else [m for m in measures if m in MEASURES_LIST] or error(
        f"Unknown measure(s): {', '.join(set(measures) - set(MEASURES_LIST))}")

    output = 'mean' if output is None else [m for m in output if m in OUTPUT_TYPE] or error(
        f"Unknown discomfort(s): {', '.join(set(output) - set(OUTPUT_TYPE))}")

    if tStart < 0: return error("Start timestamp can't be negative.")
    if tEnd < 0: return error("End timestamp can't be negative.")
    if tStart > tEnd: return error("Start timestamp can't be superior to end timestamp.")
    if not (re.match(r'^[1-9]+\d*(m|h|d|w|mo|y)$', str(tInterval))): return error(
        "Interval is not in a correct format.")

    filtered_data = predict_temperature(tStart, tEnd, tInterval, measures, salle, prediction_hour)
    return str(filtered_data[0][0])

@app.route('/window')
def window():
    return window_detection()


def regex_match(input_string, regex_pattern):
    return re.match(regex_pattern, input_string)