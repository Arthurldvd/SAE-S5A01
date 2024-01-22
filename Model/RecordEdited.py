



from datetime import datetime
from time import time


class RecordEdited:
    def __init__(self, _time, _value):
        self._time = _time
        self._value = _value

    def __str__(self):
        return (
            f"_time: {self._time}, "
            f"_value: {self._value}, "
        )

    def to_dict(self):
        data_dict = {
            'timestamp': datetime.timestamp(self._time),
            'values': self._value,
        }
        return data_dict

def to_recordEdited(data):
    return RecordEdited(
        data['_time'],
        data['_value'],
    )
