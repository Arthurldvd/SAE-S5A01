class Record:
    def __init__(self, _measurement, _field, _value, _start, _stop, _time, domain, entity_id):
        self._measurement = _measurement
        self._field = _field
        self._value = _value
        self._start = _start
        self._stop = _stop
        self._time = _time
        self.domain = domain
        self.entity_id = entity_id
        self.inconforts = []

    def __str__(self):
        return (
            f"_measurement: {self._measurement}, "
            f"_field: {self._field}, "
            f"_value: {self._value}, "
            f"_start: {self._start}, "
            f"_stop: {self._stop}, "
            f"_time: {self._time}, "
            f"domain: {self.domain}, "
            f"entity_id: {self.entity_id}, "
            f"inconforts: {self.inconforts}"
        )

    def to_dict(self):
        data_dict = {
            '_measurement': self._measurement,
            '_field': self._field,
            '_value': self._value,
            '_start': self._start,
            '_stop': self._stop,
            '_time': self._time,
            'domain': self.domain,
            'entity_id': self.entity_id
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

