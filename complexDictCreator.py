import datetime
from audioop import avg

from numpy import average

from Model.Record import Record
from clusterCreator import get_mesure


def create_dict_classified(data, harmonizeData, supressErrors, *fields):
    result = {}

    def classify_data(data, fields):
        if len(fields) == 0:
            return data

        field = fields[0]
        classified_data = []

        distinct_keys = set(getattr(entry, field) for entry in data)

        for key in distinct_keys:
            filtered_data = [x for x in data if getattr(x, field) == key]
            tabledata = {
                "id": key,
                field: classify_data(filtered_data, fields[1:])
            }
            classified_data.append(tabledata)

        return classified_data

    result = classify_data(data, fields)
    return result

def convert_datetimeKeys(data):
    if not isinstance(data, dict):
        return data

    converted_data = {}
    for key, value in data.items():
        if isinstance(key, datetime.datetime):
            key = str(key)
        if isinstance(value, dict):
            value = convert_datetimeKeys(value)
        converted_data[key] = value

    return converted_data

def convert_to_json_serializable(data):
    if isinstance(data, dict):
        return {key: convert_to_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_serializable(item) for item in data]
    elif isinstance(data, Record):
        return data.to_dict()
    else:
        return str(data)
def harmonize_data(filtered_data: [Record]):
    harmonized_data = Record(
        #_measurement
        list(set([x._measurement for x in filtered_data])),

        filtered_data[0]._field if all(
            obj._field == filtered_data[0]._field for obj in filtered_data) else "error",

        # _value
        average([x._value for x in filtered_data]),

        filtered_data[0]._start if all(
            obj._start == filtered_data[0]._start for obj in filtered_data) else "error",

        filtered_data[0]._stop if all(
            obj._stop == filtered_data[0]._stop for obj in filtered_data) else "error",

        filtered_data[0]._time if all(
            obj._time == filtered_data[0]._time for obj in filtered_data) else "error",

        filtered_data[0].domain if all(
            obj.domain == filtered_data[0].domain for obj in filtered_data) else "error",

        list(set([x.entity_id for x in filtered_data])),

        filtered_data[0].mesure if all(
            obj.mesure == filtered_data[0].mesure for obj in filtered_data) else "error",
    )
    harmonized_data.inconforts = list(set([x.inconforts for x in filtered_data if x.inconforts is not None]))
    return harmonized_data
def suppress_errors_data(filtered_data):
    return filtered_data



