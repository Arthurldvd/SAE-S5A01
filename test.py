from influxdb_client import InfluxDBClient

from incomfort_constraints import init_conditions, check_constraint
from influxdb_service import init_influxdb, request_influxBD

init_influxdb()
data = request_influxBD(
    '''from(bucket: "IUT_BUCKET")
      |> range(start: 2023-11-30T00:00:00Z, stop: 2023-12-31T23:59:59Z)
      |> filter(fn: (r) => r["_measurement"] == "ppm" or r["_measurement"] == "%" or r["_measurement"] == "°C" or r["_measurement"] == "dBA")
      |> filter(fn: (r) => r["_field"] == "value")
      |> filter(fn: (r) => r["domain"] == "sensor")
      |> filter(fn: (r) => r["entity_id"] == "d251_1_co2_carbon_dioxide_co2_level" or r["entity_id"] == "d251_1_co2_air_temperature" or r["entity_id"] == "d251_1_co2_dew_point" or r["entity_id"] == "d251_1_co2_humidity" or r["entity_id"] == "d251_1_co2_volatile_organic_compound_level")
      |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
      |> yield(name: "mean")
    '''
)

constraints = init_conditions()
# print(data)
# check_constraint(data, constraints)