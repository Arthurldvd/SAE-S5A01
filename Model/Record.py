from clusterCreator import get_mesure


class Record:
    def __init__(self, _measurement, _field, _value, _start, _stop, _time, domain, entity_id, mesure=None):
        self._measurement = _measurement
        self._field = _field
        self._value = _value
        self._start = _start
        self._stop = _stop
        self._time = _time
        self.domain = domain
        self.entity_id = entity_id
        if isinstance(entity_id, list):
            self.salle = entity_id[0].split("_")[0] if entity_id[0] is not None and entity_id[0].split("_")[0] in salles else 'tetras'
        else:
            self.salle = entity_id.split("_")[0] if entity_id is not None and entity_id.split("_")[0] in salles else 'tetras'
        self.mesure = mesure if not None else get_mesure(self)
        self.inconforts = None

    def __str__(self):
        return (
            f"_measurement: {self._measurement}, "
            f"_value: {self._value}, "
            f"_time: {self._time}, "
            f"domain: {self.domain}, "
            f"entity_id: {self.entity_id}, "
            f"salle: {self.salle}, "
            f"inconforts: {self.inconforts}"
        )

    def to_dict(self):
        data_dict = {
            # 'measurement': self._measurement,
            'value': self._value,
            # '_time': self._time,
            # 'domain': self.domain,
            # 'entity_id': self.entity_id,
            # 'salle': self.salle,
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

salles = ['d251', 'd351', 'd360']