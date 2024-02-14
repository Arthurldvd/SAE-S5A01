



from datetime import datetime
from time import time


class RecordEdited:
    def __init__(self, time, _value):
        self.time = time
        self._value = _value

    def __str__(self):
        return (
            f"time: {self.time}, "
            f"_value: {self._value}, "
        )

    def to_dict(self):
        data_dict = {
            'timestamp': datetime.timestamp(self.time),
            'values': self._value,
        }
        return data_dict

def to_recordEdited(data):
    return RecordEdited(
        data['time'],
        data['_value'],
    )
