import datetime

from Model.Record import Record


def create_dict_classified(data, *fields):
    result = {}

    def classify_data(data, fields):
        if len(fields) == 0:
            return data

        field = fields[0]
        classified_data = {}

        distinct_keys = set(getattr(entry, field) for entry in data)

        for key in distinct_keys:
            filtered_data = [x for x in data if getattr(x, field) == key]
            classified_data[key] = classify_data(filtered_data, fields[1:])

        return classified_data

    result = classify_data(data, fields)
    return result

def convert_datetimeKeys(data):
    if not isinstance(data, dict):
        return data

    converted_data = {}
    for key, value in data.items():
        if isinstance(key, datetime.datetime):
            key = key.strftime('%m/%d/%Y')
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
