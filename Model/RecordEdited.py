class RecordEdited:
    def __init__(self, _time, _value, inconforts):
        self._time = _time
        self._value = _value
        self.inconforts = inconforts

    def __str__(self):
        return (
            f"_time: {self._time}, "
            f"_value: {self._value}, "
            f"inconforts: {self.inconforts}"
        )

    def to_dict(self):
        data_dict = {
            '_time': self._time,
            '_value': self._value,
            'inconforts': self.inconforts
        }
        return data_dict

def to_recordEdited(data):
    return RecordEdited(
        data['_time'],
        data['_value'],
        data['inconforts']
    )
