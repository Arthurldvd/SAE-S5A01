class Mesure:
    def __init__(self, name, conditions):
        self.name = name
        self.conditions = conditions

def get_mesure(record):
    mesure_name = next((mesure.name for mesure in mesures if mesure.conditions(record)), None)
    if callable(mesure_name):
        return mesure_name(record)
    return mesure_name

mesures = [
    Mesure('Humidité', lambda record: record._measurement == '%' and record.entity_id != 'd351_1_multisensor9_smoke_density'),
    Mesure('Fumée', lambda record: record._measurement == '%' and record.entity_id == 'd351_1_multisensor9_smoke_density'),
    Mesure(lambda record: record._measurement, lambda record: record._measurement.startswith('binary_sensor')),
    Mesure('Décibels', lambda record: record._measurement == 'dBA'),
    Mesure('Luminosité', lambda record: record._measurement == 'lx'),
    Mesure('Co2', lambda record: record._measurement == 'ppm' and record.entity_id.endswith('co2_level')),
    Mesure('Co2 Volatil', lambda record: record._measurement == 'ppm' and record.entity_id.endswith('organic_compound_level')),
    Mesure('Température', lambda record: record._measurement == '°C' and (lambda record: record.entity_id.endswith('air_temperature') or record.entity_id.endswith('air_temperature_2'))),
    Mesure('co2 Dew', lambda record: record._measurement == '°C' and record.entity_id.endswith('co2_dew_point')),
    Mesure('Particules', lambda record: record._measurement == 'µg/m³')
]
