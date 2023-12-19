from influxdb_client import InfluxDBClient

client = InfluxDBClient(
    url = '51.83.36.122:8086',
    token = 'q4jqYhdgRHuhGwldILZ2Ek1WzGPhyctQ3UgvOII-bcjEkxqqrIIacgePte33CEjekqsymMqWlXnO0ndRhLx19g==',
    org = 'INFO',
    bucket = 'iut_bucket'
    )

print(client.health())