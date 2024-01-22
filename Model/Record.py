class Record:
    def __init__(self, _measurement, _field, _value, _start, _stop, _time, domain, entity_id):
        self._measurement = _measurement
        self._value = _value
        self._time = _time
        self.domain = domain
        self.entity_id = entity_id
        self.inconforts = []

    def __str__(self):
        return (
            f"_measurement: {self._measurement}, "
            f"_value: {self._value}, "
            f"_time: {self._time}, "
            f"domain: {self.domain}, "
            f"entity_id: {self.entity_id}, "
            f"inconforts: {self.inconforts}"
        )

    def to_dict(self):
        data_dict = {
            'measurement': self._measurement,
            'value': self._value,
            #'_time': self._time,
            #'domain': self.domain,
            'sensorId': self.entity_id,
            'discomfortList': self.inconforts
        }
        return data_dict

def to_record(data):
    return Record(
        data['_measurement'],
        data['_field'],
        data['_value'],
        data['_start'],
        data['_stop'],
        data['_time'],
        data['domain'],
        data['entity_id']
    )