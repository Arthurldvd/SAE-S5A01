from flask import Flask, request, jsonify

app = Flask(__name__)

def parseArray(array):
    return [value for value in array.split(',')]

def error(message: str):
    return {
        'error' : message
    }

@app.route('/data')
def data():
    required_args = ['start', 'end', 'interval', 'mesures', 'incomfort']
    for arg in required_args:
        if arg not in request.args:
            return error(f'Missing argument : {arg}')
        
    # Getting parameters
    tStart = int(request.args.get('start'))
    tEnd = int(request.args.get('end'))
    tInterval = int(request.args.get('interval'))
    mesures = request.args.get('mesures')
    incomfort = request.args.get('incomfort')
    parsed_mesures = parseArray(mesures)
    parsed_incomfort = parseArray(incomfort)

    # Verification
    if (tStart < 0): return error("Start timestamp can't be negative")
    if (tEnd < 0): return error("End timestamp can't be negative")
    if (tInterval < 0): return error("End timestamp can't be negative")
    if (tStart > tEnd): return error("Start timestamp can't be superior to end timestamp")

    return jsonify({
        'Mesure filters': parsed_mesures,
        'Incomfort filters': parsed_incomfort,
        'Timestamp start': tStart,
        'Timestamp end': tEnd,
        'Interval': f'{tInterval} minutes'
    })

if __name__ == '__main__':
    app.run(debug=True)