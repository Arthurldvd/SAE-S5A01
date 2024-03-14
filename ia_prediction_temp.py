import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import numpy as np
import tensorflow as tf
from keras.src.callbacks import Callback, ModelCheckpoint
from keras.src.engine.input_layer import InputLayer
from keras.src.optimizers import Adam
from keras.src.saving.saving_api import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

from influxdb_service import filter_data, init_influxdb

NUMBER_EPOCHS = 30
PACKET_SIZE = 6
MODEL_PATH = "./ia_model/temperature"

def train_temperature(tStart, tEnd, tInterval, measures, salle, prediction_hour):
    init_influxdb()
    #1 retourner un object comme dans IA.py (projet externe)
    #2 train le modèle avec une requête qui récupère TOUTES les températures de toutes les heures
    #3 prédire une heure en précisant l'heure, la prédiction se fera sur les x heures précedentes qui
    # ont du sens
    #4 filtrer la requete sur une seule salle
    data = get_training_data(tStart, tEnd, tInterval, measures, salle)
    return train_ai_temperature(data_for_training(data, PACKET_SIZE), datetime.fromtimestamp(int(prediction_hour)))

def get_training_data(tStart, tEnd, tInterval, measures, salle):
    # request = '''
    # from(bucket: "IUT_BUCKET")
    #   |> range(start: 1700703993, stop: 1703172412)
    #   |> filter(fn: (r) => r["_measurement"] == "°C")
    #   |> filter(fn: (r) => r["_field"] == "value")
    #   |> filter(fn: (r) => r["domain"] == "sensor")
    #   |> filter(fn: (r) => r["entity_id"] == "d251_1_co2_air_temperature")
    #   |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
    #   |> yield(name: "mean")'''
    data = filter_data(tStart, tEnd, tInterval, measures, salle)
    data.sort(key=lambda x: x.time)
    return data

def data_for_training(data, packet_size):
    data_for_training = []
    for i in range(len(data) - packet_size):
        DFT = {
            'previous_temp': [d._value for d in data[i:i + packet_size]],
            'previous_hours': [uni_date(d.time) for d in data[i:i + packet_size]],
            'expected_temp': data[i + packet_size]._value
        }
        data_for_training.append(DFT)

    return data_for_training

def train_ai_temperature(data_training, prediction_hour):
    prediction_hour = uni_date(prediction_hour)
    X, y = create_sequences_with_targets(data_training)

    model = Sequential()
    model.add(InputLayer((2, 6)))
    model.add(LSTM(100, return_sequences=True))
    model.add(LSTM(100, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='linear'))
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse')

    class PredictionsCallback(Callback):
        def __init__(self, input_sequence):
            self.input_sequence = input_sequence

        def on_epoch_end(self, epoch, logs=None):
            global LAST_EPOCH_RESULT
            predicted_temperature = self.model.predict(np.array(self.input_sequence), verbose=0)
            print(f"Epoch {epoch + 1} - Predicted Temperature: {predicted_temperature[0, 0]}")
            if epoch + 1 == NUMBER_EPOCHS:
                print(predicted_temperature)
                LAST_EPOCH_RESULT = predicted_temperature

    # -------------------------------- A VIRER QUAND LE MODELE MARCHE -------------------------------------
    input_sequence_entry = max(np.where(np.array([_x == prediction_hour for _x in X]))[0])
    print(f"NOUS VOULONS PREDIRE :  {y[input_sequence_entry]}")

    input_sequence = [np.array(X[input_sequence_entry][0]), np.array(X[input_sequence_entry][1])]
    input_sequence = np.array(input_sequence)
    input_sequence = input_sequence.reshape(-1, 2, PACKET_SIZE)
    # -------------------------------- A VIRER QUAND LE MODELE MARCHE -------------------------------------

    predictions_callback = PredictionsCallback(input_sequence)
    model.fit(X, y, epochs=NUMBER_EPOCHS, batch_size=1, verbose=2, callbacks=[predictions_callback])
    model.save(MODEL_PATH)

    return LAST_EPOCH_RESULT

def test_temperature(prediction_hour_b, prediction_hour_b_e):
    model = load_model(MODEL_PATH)

    number_hours = int((datetime.fromtimestamp(int(prediction_hour_b_e)) -
                        datetime.fromtimestamp(int(prediction_hour_b))).total_seconds() / 3600)
    tStart = (datetime.fromtimestamp(int(prediction_hour_b)) - timedelta(hours=PACKET_SIZE)).timestamp()
    tEnd = datetime.fromtimestamp(int(prediction_hour_b_e)).timestamp()
    data = filter_data(int(tStart), int(tEnd), "1h", ["Température"], "d251_1_co2_air_temperature")

    data_testing = data_for_training(data, PACKET_SIZE)
    X_test, y_test = create_sequences_with_targets(data_testing)

    result = []
    for i in range(len(X_test)):
        result.append(test_ai_temperature_u(model, X_test[i], y_test[i], (
            datetime.fromtimestamp(int(tStart)) + timedelta(hours=PACKET_SIZE+i)).timestamp())
        )

    print(result)

    #-------------------------------------#
    plt.plot(
        [x.time.strftime("%m-%d %H:%M") for x in data if x.time.replace(tzinfo=None) >= datetime.fromtimestamp(int(prediction_hour_b))],
        [x._value for x in data if x.time.replace(tzinfo=None) >= datetime.fromtimestamp(int(prediction_hour_b))],
        label='List 1'
    )
    plt.plot(
        [x[1].strftime("%m-%d %H:%M") for x in result if x[1].replace(tzinfo=None) >= datetime.fromtimestamp(int(prediction_hour_b))],
        [x[0] for x in result if x[1].replace(tzinfo=None) >= datetime.fromtimestamp(int(prediction_hour_b))],
        label='List 2'
    )

    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Comparison of List 1 and List 2')
    plt.legend()

    plt.xticks(rotation=45)
    plt.show()

def test_ai_temperature_u(model, X_test, y_test, prediction_hour):
    prediction_hour_final = prediction_hour
    prediction_hour = uni_date(datetime.fromtimestamp(int(prediction_hour)))

    X_test = np.array(X_test.reshape(-1, 2, PACKET_SIZE))
    y_test = np.array([y_test])

    loss = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss}")

    predicted_temperature = model.predict(np.array(X_test), verbose=0)
    return predicted_temperature[0][0], datetime.fromtimestamp(prediction_hour_final)

def create_sequences_with_targets(data):
    sequences = []
    targets = []
    for entry in data:
        sequences.append((entry['previous_hours'], entry['previous_temp']))
        targets.append(entry['expected_temp'])
    return np.array(sequences), np.array(targets)

def uni_date(datetime):
    return int(datetime.strftime('%H'))

train_temperature("1704096000", "1709798400", "1h", ["Température"], "d251_1_co2_air_temperature", "1709794800")
test_temperature("1709794800", "1709852400")

