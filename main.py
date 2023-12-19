from influxdb_client import InfluxDBClient
from influxdb_service import init_influxdb, request_influxBD

init_influxdb()
data = request_influxBD(
    '''from(bucket: "IUT_BUCKET")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "%")
      |> filter(fn: (r) => r["_field"] == "value")
      |> filter(fn: (r) => r["domain"] == "sensor")
      |> filter(fn: (r) => r["entity_id"] == "d251_1_co2_humidity" or r["entity_id"] == "d251_1_multisensor_humidity" or r["entity_id"] == "d351_1_co2_humidity" or r["entity_id"] == "d351_1_multisensor9_humidity" or r["entity_id"] == "d351_1_multisensor9_smoke_density" or r["entity_id"] == "d351_1_multisensor_humidity" or r["entity_id"] == "d351_2_multisensor_humidity" or r["entity_id"] == "d351_2_co2_humidity" or r["entity_id"] == "d351_3_co2_humidity" or r["entity_id"] == "d360_1_co2_humidity" or r["entity_id"] == "d360_1_multisensor_humidity_2")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
      |> yield(name: "mean")'''
)

tables = query_api.query('from(bucket: "IUT_BUCKET") |> range(start: -1h)')

results = []
for table in tables:
  for record in table.records:
    results.append((record.get_field(), record.get_value()))

print(results)