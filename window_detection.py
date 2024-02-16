from complexDictCreator import create_dict_classified
from influxdb_service import request_influxBD, init_influxdb
from functools import reduce

def window_detection():
    init_influxdb()
    data = request_influxBD(
        f'''    
        from(bucket: "IUT_BUCKET")
          |> range(start: 1707404067, stop: 1708008870)
          |> filter(fn: (r) => r["_measurement"] == "°C" or r["_measurement"] == "µg/m³" or r["_measurement"] == "UV index")
          |> filter(fn: (r) => r["_field"] == "value")
          |> filter(fn: (r) => r["domain"] == "sensor")
          |> aggregateWindow(every: 20m, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
    )

    data = create_dict_classified(data, False, False, "time")

    stored_scores = []

    for i in range(10, len(data)):
        entities = list(set(x.entity_id for y in data[i - 10: i] for x in y))
        entities = [e for e in entities if ([x.entity_id for y in data[i - 10: i] for x in y].count(e) == 10)]
        lists = [[(x._value) for y in data[i - 10: i] for x in y if x.entity_id == e] for e in entities]

        final_result = sum([sum(abs(sublist[i] - sublist[i + 1]) for i in range(len(sublist) - 1)) for sublist in lists])
        stored_scores.append(final_result)

    indexes = [index for index, value in enumerate(stored_scores) if value > 17]

    borne_inferieur = [indexes[i] for i in range(len(indexes) - 1) if indexes[i + 1] - indexes[i] != 1]
    borne_superieur = [indexes[i] for i in range(1, len(indexes)) if indexes[i] - indexes[i - 1] != 1]

    common_elements = set(borne_inferieur) & set(borne_superieur)
    split_index = [x for x in [indexes[0]] + borne_inferieur + borne_superieur + [indexes[len(indexes) - 1]] if x not in common_elements]

    split_index = sorted(list(set(split_index)))

    list_final_time = []

    for i in range(0, int((len(split_index) + 1) / 2)):
        list_final_time.append(
            {
                "Ouverture de la fenêtre": data[split_index[i * 2]][0].time,
                "Fermeture de la fenêtre": data[split_index[i * 2 + 1]][0].time,
            }
        )

    return list_final_time


window_detection()