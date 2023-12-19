class Constraint:
    def __init__(self, field, conditions):
        self.field = field
        self.conditions = conditions

def init_conditions():
    constraints = [
        Constraint('d251_1_co2_air_temperature', lambda data: data > 21),
        Constraint('d251_1_co2_air_temperature', lambda data: data < 19),
        Constraint('d251_1_co2_carbon_dioxide_co2_level', lambda data: data > 5000),
        Constraint('d251_1_co2_dew_point', lambda data: data > 10),
        Constraint('d251_1_co2_humidity', lambda data: data > 50)
    ]

    return constraints

def check_constraint(data, constraints):
    print(data)