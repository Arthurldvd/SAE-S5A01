from Model import Record
from Model.Inconfort import Inconfort


class Constraint:
    def __init__(self, field, conditions, description):
        self.field = field
        self.conditions = conditions
        self.description = description

def init_conditions():
    constraints = [
        Constraint('d251_1_co2_air_temperature', lambda data: data > 21, "La température excède 21°"),
        Constraint('d251_1_co2_air_temperature', lambda data: data < 19, "La température baisse 19°"),
        Constraint('d251_1_co2_carbon_dioxide_co2_level', lambda data: data > 5000, "La concentration de CO2 dépasse 5000°"),
        Constraint('d251_1_co2_dew_point', lambda data: data > 10, "Le niveau de décibel dépasse 10°"),
        Constraint('d251_1_co2_humidity', lambda data: data > 50, "Le taux d'humidité dépasse 50%")
    ]

    return constraints

def check_constraint(data: Record, constraints):
    data.sort(key=lambda x: x._start)
    for constraint in constraints:
        data_field = [x for x in data if x.entity_id == constraint.field]
        data_field_constraint = [x for x in data_field if constraint.conditions(x._value)]
        for record in data_field_constraint:
            inconfort = Inconfort(record._value, constraint.description)
            record.inconforts.append(inconfort)


