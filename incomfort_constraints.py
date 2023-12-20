from itertools import groupby

from Model import Record
from Model.Inconfort import Inconfort
from Model.RecordEdited import RecordEdited


class Constraint:
    def __init__(self, field, conditions, description, type):
        self.field = field
        self.conditions = conditions
        self.description = description
        self.type = type

def init_conditions():
    constraints = [
        Constraint('°C', lambda data: data > 21, "La température excède 21°", "temperature"),
        Constraint('°C', lambda data: data < 19, "La température baisse 19°", "temperature"),
        Constraint('ppm', lambda data: data > 5000, "La concentration de CO2 dépasse 5000°", "co2"),
        Constraint('dBA', lambda data: data > 10, "Le niveau de décibel dépasse 10°", "db"),
        Constraint('%', lambda data: data > 50, "Le taux d'humidité dépasse 50%", "humidity"),
        Constraint('µg/m³', lambda data: data > 10, "Le niveau de particules dépasse 10 µg/m³", "co2")
    ]

    return constraints

def get_constraints(filter=None):
    if filter is None:
        return init_conditions()
    return [c for c in init_conditions() if c.type in filter]

def check_constraint(data: Record, constraints):
    distinct_times = set(entry._time for entry in data)

    record_edited = []
    for time in distinct_times:
        records = []
        data_field = [x for x in data if x._time == time]

        for constraint in get_constraints(constraints):
            [setattr(x, 'inconforts', Inconfort(x._value, constraint.description).to_dict()) for x in data_field
             if x._measurement == constraint.field and constraint.conditions(x._value)]

        records.extend([x.to_dict() for x in data_field])
        record_edited.append(RecordEdited(time, records).to_dict())

    return record_edited



