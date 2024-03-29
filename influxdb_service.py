from functools import reduce

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

def filter_data(tStart, tEnd, tInterval, measures, salle, output="mean"):
    #|> filter(fn: (r) => r["_measurement"] =~ {measures})
    # measures = convert_regex(measures)
    bucket = "IUT_BUCKET"

    init_influxdb()
    request = f'''
    import "strings"
    import "regexp"

    from(bucket: "{bucket}")
          |> range(start: {tStart}, stop: {tEnd})
          |> filter(fn: (r) => r["_field"] == "value")
          |> filter(fn: (r) => strings.hasPrefix(v: r["entity_id"], prefix: "{salle}"))
          |> aggregateWindow(every: {tInterval}, fn: mean, createEmpty: false)
          |> yield(name: "{output}")
        '''

    print(request)
    return [x for x in request_influxBD(request) if x.mesure in measures]

def convert_regex(table):
    table = [element.replace('/', '\/') for element in table]

    if isinstance(table, list):
        return "/" + reduce(lambda acc, val: f'{acc}|{val}', map(str, table)) + "/"
    return table