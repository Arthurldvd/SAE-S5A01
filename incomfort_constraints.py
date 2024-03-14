from itertools import groupby

from Model import Record
from Model.Inconfort import Information
from Model.RecordEdited import RecordEdited
from complexDictCreator import create_dict_classified, convert_to_json_serializable
from influxdb_service import filter_data


class ConditionsInfo:
    def __init__(self, code, field, conditions, description, type, isDisconfort):
        self.code = code
        self.field = field
        self.conditions = conditions
        self.description = description
        self.type = type
        self.isDisconfort = isDisconfort

def init_conditions():
    conditions_to_check = [
        # Constraints
        ConditionsInfo('TG21', 'Température', lambda data: data > 21, "La température excède 21°", "temperature", True),
        ConditionsInfo('TL19', 'Température', lambda data: data < 19, "La température baisse 19°", "temperature", True),
        ConditionsInfo('CG18', 'co2 Dew', lambda data: data > 18, "La salle contient bcp de CO2 humide", "co2", True), #!!!!
        ConditionsInfo('CL05', 'co2 Dew', lambda data: data < 5, "La salle est sèche", "co2", True), # !!!!
        ConditionsInfo('CG5K', 'Co2', lambda data: data > 2000, "La concentration de CO2 dépasse 2000°", "co2", True),
        ConditionsInfo('CG5K', 'Co2 Volatile', lambda data: data > 2, "La quantité de CO2 volatile dépasse 2", "co2", True), # !!!!
        ConditionsInfo('DL10', 'Décibels', lambda data: data > 10, "Le niveau de décibel dépasse 10°", "db", True),
        ConditionsInfo('HG50', 'Humidité', lambda data: data > 50, "Le taux d'humidité dépasse 50%", "humidity", True),
        ConditionsInfo('HG50', 'Fumée', lambda data: data > 50, "Le taux de fumée dépasse 50%", "fumee", True), # !!!!
        ConditionsInfo('HG50', 'Luminosité', lambda data: data > 50, "Le taux de lumière dépasse 50%", "luminosite", True),
        ConditionsInfo('PG10', 'Particules', lambda data: data > 10, "Le niveau de particules dépasse 10 µg/m³", "particules", True), # !!!!

        ConditionsInfo('BSHP', 'binary_sensor.d251_1_co2_highly_polluted', lambda data: data == 1, "La salle est très polluée", "co2", True),
        ConditionsInfo('BSHP', 'binary_sensor.d231_1_co2_highly_polluted', lambda data: data == 1, "La salle est très polluée", "co2", True),
        ConditionsInfo('BSHP', 'binary_sensor.d351_2_co2_highly_polluted', lambda data: data == 1, "La salle est très polluée", "co2", True),
        ConditionsInfo('BSHP', 'binary_sensor.d360_1_co2_highly_polluted', lambda data: data == 1, "La salle est très polluée", "co2", True),

        # Information
        ConditionsInfo('BSPD', 'binary_sensor.d251_1_multisensor_motion_detection', lambda data: data == 1, "Personnes présentes",
                       "co2", False),
        ConditionsInfo('BSPD', 'binary_sensor.d231_1_multisensor_motion_detection', lambda data: data == 1, "Personnes présentes",
                       "co2", False),
        ConditionsInfo('BSPD', 'binary_sensor.d351_2_multisensor_motion_detection', lambda data: data == 1, "Personnes présentes",
                       "co2", False),
        ConditionsInfo('BSPD', 'binary_sensor.d360_1_multisensor_motion_detection', lambda data: data == 1, "Personnes présentes",
                       "co2", False),
    ]

    return conditions_to_check

def get_constraints(filter=None):
    if filter is None:
        return init_conditions()
    return [c for c in init_conditions() if c.type in filter]

def modify_object(data: Record, constraints, harmonizeData, supressError):
    print([x._value for x in data])
    # POUR CHAQUE TEMPS, AJOUT DE CONTRAINTES SI UNE DES CONTRAINTES PROBLEME
    for constraint in get_constraints(constraints):
        [setattr(x, 'inconforts', constraint.code) for x in data
        if x.mesure == constraint.field and constraint.conditions(x._value)]

    # DICTIONNAIRE / REUNISSEMENT DES DONNEES (GROUP BY) EN FONCTION DU TEMPS
    classified_data = create_dict_classified(data, harmonizeData, supressError, "salle", "time", "mesure")
    classified_data = convert_to_json_serializable(classified_data)
    return classified_data

MEASURES_LIST = ['%', 'dBA', 'ppm', '°C', 'µg/m³', 'lx',
                 "binary_sensor.d251_1_co2_highly_polluted",
                 "binary_sensor.d251_1_co2_moderately_polluted",
                 "binary_sensor.d251_1_co2_slightly_polluted",
                 "binary_sensor.d251_1_multisensor_motion_detection",
                 "binary_sensor.d351_1_co2_highly_polluted",
                 "binary_sensor.d351_1_co2_moderately_polluted",
                 "binary_sensor.d351_1_co2_slightly_polluted",
                 "binary_sensor.d351_1_multisensor_motion_detection",
                 "binary_sensor.d351_2_co2_highly_polluted",
                 "binary_sensor.d351_2_co2_moderately_polluted",
                 "binary_sensor.d351_2_co2_slightly_polluted",
                 "binary_sensor.d351_2_multisensor_motion_detection",
                 "binary_sensor.d360_1_co2_highly_polluted"
                 "binary_sensor.d360_1_co2_moderately_polluted"
                 "binary_sensor.d360_1_co2_slightly_polluted"
                 "binary_sensor.d360_1_co2_multisensor_motion_detection"]

filtered_data = filter_data("IUT_BUCKET", "1700703993", "1703172412", "1h", MEASURES_LIST, "", "mean")
filtered_data = modify_object(filtered_data, None, True, False)


