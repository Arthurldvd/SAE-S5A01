from influxdb_client import InfluxDBClient

client = InfluxDBClient(
    url = '51.83.36.122:8086',
    token = 'q4jqYhdgRHuhGwldILZ2Ek1WzGPhyctQ3UgvOII-bcjEkxqqrIIacgePte33CEjekqsymMqWlXnO0ndRhLx19g==',
    org = 'INFO',
    bucket = 'iut_bucket'
    )

query_api = client.query_api()
tables = query_api.query('from(bucket: "IUT_BUCKET") |> range(start: -1h)')