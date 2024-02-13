class Mesure:
    def __init__(self, name, conditions):
        self.name = name
        self.conditions = conditions

def get_mesure(record):
    return next((mesure.name for mesure in mesures if mesure.conditions(record)), None)

mesures = [
    Mesure('Mesure d\'humidié dans l\'air en %', lambda record: record._measurement == '%' and record.entity_id != 'd351_1_multisensor9_smoke_density'),
    Mesure('Mesure de fumée dans l\'air en %', lambda record: record._measurement == '%' and record.entity_id == 'd351_1_multisensor9_smoke_density'),
    Mesure(lambda record: record._measurement, lambda record: record._measurement.startswith('binary_sensor')),
    Mesure('Mesure de décibels', lambda record: record._measurement == 'dBA'),
    Mesure('Mesure de luminosité en lx', lambda record: record._measurement == 'lx'),
    Mesure('Mesure de co2 en ppm', lambda record: record._measurement == 'ppm' and record.entity_id.endswith('co2_level')),
    Mesure('Mesure de co2 volatil en ppm', lambda record: record._measurement == 'ppm' and record.entity_id.endswith('organic_compound_level')),
    Mesure('Mesure de la température de l\'air', lambda record: record._measurement == '°C' and (lambda record: record.entity_id.endswith('air_temperature') or record.entity_id.endswith('air_temperature_2'))),
    Mesure('co2 dew point ?', lambda record: record._measurement == '°C' and record.entity_id.endswith('co2_dew_point')),
    Mesure('Mesure du taux de particules', lambda record: record._measurement == 'µg/m³')
]
