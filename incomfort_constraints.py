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
        Constraint('d251_1_co2_air_temperature', lambda data: data > 21, "La température excède 21°", "temperature"),
        Constraint('d251_1_co2_air_temperature', lambda data: data < 19, "La température baisse 19°", "temperature"),
        Constraint('d251_1_co2_carbon_dioxide_co2_level', lambda data: data > 5000, "La concentration de CO2 dépasse 5000°", "co2"),
        Constraint('d251_1_co2_dew_point', lambda data: data > 10, "Le niveau de décibel dépasse 10°", "db"),
        Constraint('d251_1_co2_humidity', lambda data: data > 50, "Le taux d'humidité dépasse 50%", "humidity")
    ]

    return constraints

def get_constraints(filter=None):
    if filter is None:
        return init_conditions()
    return [c for c in init_conditions() if c.type in filter]

def check_constraint(data: Record, constraints):
    distinct_times = set(entry._time for entry in data)
    recordEdited = []
    for time in distinct_times:
        records = []
        inconforts = []
        for constraint in get_constraints(constraints):
             data_field = [x for x in data if x._time == time]
             records.extend([x.to_dict() for x in data_field])
             data_field_constraint = [x for x in data_field if x.entity_id == constraint.field and constraint.conditions(x._value)]
             for record in data_field_constraint:
                 inconfort = Inconfort(record._value, constraint.description)
                 inconforts.append(inconfort.to_dict())
        print(records)
        print(records[0])
        recordEdited.append(RecordEdited(time, records, inconforts))

    return [x.to_dict() for x in recordEdited]
    # for constraint in get_constraints(constraints):
    #     data_field = [x for x in data if x.entity_id == constraint.field]
    #     data_field_constraint = [x for x in data_field if constraint.conditions(x._value)]
    #     for record in data_field_constraint:
    #         # print(record)
    #         inconfort = Inconfort(record._value, constraint.description)
    #         record.inconforts.append(inconfort.__str__())
    #
    # grouped_data = {key: list(group) for key, group in groupby(data, key=lambda x: x._time)}
    # print(grouped_data)
    # return [x.to_dict() for x in data]


