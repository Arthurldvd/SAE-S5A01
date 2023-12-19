from influxdb_client import InfluxDBClient

query_api = None

def init_influxdb():
    client = InfluxDBClient(
        url = '51.83.36.122:8086',
        token = 'q4jqYhdgRHuhGwldILZ2Ek1WzGPhyctQ3UgvOII-bcjEkxqqrIIacgePte33CEjekqsymMqWlXnO0ndRhLx19g==',
        org = 'INFO',
        bucket = 'iut_bucket'
        )

    query_api = client.query_api()

def request_influxBD(query_string):
    tables = query_api.query(query_string)
    return [(record.get_field(), record.get_value()) for table in tables for record in table.records]


