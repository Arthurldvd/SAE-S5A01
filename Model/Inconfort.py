from Model import Record


class Information:
    def __init__(self, _value, _description, _isDisconfort):
        self._value = _value,
        self._description = _description
        self._isDisconfort = _isDisconfort

    def __str__(self):
        return f"_description: {self._description}, _value: {self._value}, _isDisconfort: {self._isDisconfort}"

    def to_dict(self):
        data_dict = {
            '_value': self._value,
            '_description': self._description,
            '_isDisconfort': self._isDisconfort,
        }
        return data_dict

def to_information(data):
    return Information(
        data['_value'],
        data['_description'],
        data['_disconfort'],
    )
