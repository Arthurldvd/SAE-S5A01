from flask import Flask
from flask import request

from data_types import DataTypes

app = Flask(__name__)

@app.route('/data/<type>')
def data(type: DataTypes):
    tStart = request.args.get('start')
    tEnd = request.args.get('end')
    if (tStart in [None, ""]): 
      return "You must specifiy a start date."
    if (tEnd in [None, ""]):
       return "You must specify a end date."
    if (tStart > tEnd):
       return "Start date is superior to end date."
    
    return f'{type}, {tStart}, {tEnd}'

