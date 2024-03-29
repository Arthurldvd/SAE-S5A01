import datetime
from audioop import avg

from numpy import average, where, abs
from Model.Record import Record
from scipy.stats import zscore

def create_dict_classified(data, harmonizeData, *fields):

    def classify_data(data, fields):
        if len(fields) == 0:
            return data

        field = fields[0]
        classified_data = []

        distinct_keys = sorted(set(getattr(entry, field) for entry in data))

        for key in distinct_keys:
            if len(fields) == 1:
                filtered_data = [x for x in data if getattr(x, field) == key]
                tabledata = classify_data_last_field(filtered_data)
                classified_data.append(tabledata)
            else:
                filtered_data = [x for x in data if getattr(x, field) == key]
                tabledata = {
                    field: key,
                    "values": classify_data(filtered_data, fields[1:])
                }
                classified_data.append(tabledata)

        return classified_data
    def classify_data_last_field(filtered_data):
        if harmonizeData:
            filtered_data = harmonize_data(filtered_data)

        return filtered_data

    result = classify_data(data, fields)
    return result

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

        filtered_data[0].time if all(
            obj.time == filtered_data[0].time for obj in filtered_data) else "error",

        filtered_data[0].domain if all(
            obj.domain == filtered_data[0].domain for obj in filtered_data) else "error",

        list(set([x.entity_id for x in filtered_data])),

        filtered_data[0].mesure if all(
            obj.mesure == filtered_data[0].mesure for obj in filtered_data) else "error",
    )
    harmonized_data.inconforts = list(set([x.inconforts for x in filtered_data if x.inconforts is not None]))
    return harmonized_data

def suppress_errors_data(filtered_data):
    THRESHOLD = 2.5

    z_scores = zscore([x._value for x in filtered_data])
    print(z_scores)
    obsolete_data_index = [index for index, value in enumerate(z_scores) if abs(value) > THRESHOLD]
    filtered_data = [value for index, value in enumerate(filtered_data) if index not in obsolete_data_index]
    return filtered_data



