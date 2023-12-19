from flask import Flask, request, jsonify

app = Flask(__name__)

MESURES_LIST = ['co2', 'humidity', 'uv', 'db', 'temperature']

def parseArray(array):
    parsed_array = array.split(',')
    parsed_array = [value for value in parsed_array]
    return parsed_array

def error(message: str):
    return {
        'error' : message
    }

@app.route('/data')
def data():
    required_args = ['start', 'end', 'interval']
    for arg in required_args:
        if arg not in request.args:
            return error(f'Missing argument : {arg}')
    
    # Getting parameters
    tStart = int(request.args.get('start'))
    tEnd = int(request.args.get('end'))
    tInterval = int(request.args.get('interval'))
    mesures = request.args.get('mesures')
    discomfort = request.args.get('discomfort')
    salle = request.args.get('salle')

    # Verification
    mesuresArgs = [mesures, discomfort]
    for i in range(len(mesuresArgs)):
        if mesuresArgs[i] is None:
            mesuresArgs[i] = MESURES_LIST
        else:
            for m in mesuresArgs[i]:
                if (m not in MESURES_LIST):
                    return error(f"'{m}' is not a known mesure.")

    if (tStart < 0): return error("Start timestamp can't be negative")
    if (tEnd < 0): return error("End timestamp can't be negative")
    if (tInterval < 0): return error("End timestamp can't be negative")
    if (tStart > tEnd): return error("Start timestamp can't be superior to end timestamp")

    return jsonify({
        'Mesure filters': mesures,
        'Incomfort filters': discomfort,
        'Timestamp start': tStart,
        'Timestamp end': tEnd,
        'Interval': f'{tInterval} minutes'
    })

if __name__ == '__main__':
    app.run(debug=True)