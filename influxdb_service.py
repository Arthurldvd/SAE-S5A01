from influxdb_client import InfluxDBClient
from Model.Record import to_record

query_api = None


def init_influxdb():
    global query_api
    client = InfluxDBClient(
        url='51.83.36.122:8086',
        token='q4jqYhdgRHuhGwldILZ2Ek1WzGPhyctQ3UgvOII-bcjEkxqqrIIacgePte33CEjekqsymMqWlXnO0ndRhLx19g==',
        org='INFO',
        bucket='iut_bucket'
    )

    query_api = client.query_api()


def request_influxBD(query_string):
    tables = query_api.query(query_string)
    data = []

    for table in tables:
        for record in table.records:
            data.append(to_record(record))

    return data