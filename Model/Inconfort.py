from Model import Record


class Inconfort:
    def __init__(self, _value, _description):
        self._value = _value,
        self._description = _description

    def to_inconfort(self):
        data_dict = {
            '_value': self._value,
            '_description': self._description,
        }
        return data_dict

    def __str__(self):
        return f"_description: {self._description}, _value: {self._value}"

    def to_dict(self):
        data_dict = {
            '_value': self._value,
            '_description': self._description,
        }
        return data_dict

def to_inconfort(data):
    return Inconfort(
        data['_value'],
        data['_description'],
    )
