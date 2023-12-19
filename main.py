from influxdb import InfluxDBClient

client = InfluxDBClient(
    host='51.83.36.122',
    port=8086,
    username='mbetti',
    password='JeSorsDesNoiresAAtome!',
    )

print(client.get_list_database())