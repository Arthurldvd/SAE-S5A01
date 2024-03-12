import os
from datetime import datetime, timedelta

import numpy as np
import tensorflow as tf
from keras.src.callbacks import Callback, ModelCheckpoint
from keras.src.engine.input_layer import InputLayer
from keras.src.optimizers import Adam
from keras.src.saving.saving_api import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

from influxdb_service import filter_data, init_influxdb

NUMBER_EPOCHS = 200
PACKET_SIZE = 6
MODEL_PATH = "./ia_model/lumiere"

def train_lumiere(tStart, tEnd, tInterval, measures, salle, prediction_hour):
    init_influxdb()
    #1 retourner un object comme dans IA.py (projet externe)
    #2 train le modèle avec une requête qui récupère TOUTES les températures de toutes les heures
    #3 prédire une heure en précisant l'heure, la prédiction se fera sur les x heures précedentes qui
    # ont du sens
    #4 filtrer la requete sur une seule salle
    data = get_training_data(tStart, tEnd, tInterval, measures, salle)
    return train_ai_lumiere(data_for_training(data), datetime.utcfromtimestamp(int(prediction_hour)))

def get_training_data(tStart, tEnd, tInterval, measures, salle):
    # request = '''
    # from(bucket: "IUT_BUCKET")
    #   |> range(start: 1700703993, stop: 1703172412)
    #   |> filter(fn: (r) => r["_measurement"] == "°C")
    #   |> filter(fn: (r) => r["_field"] == "value")
    #   |> filter(fn: (r) => r["domain"] == "sensor")
    #   |> filter(fn: (r) => r["entity_id"] == "d251_1_co2_air_lumiere")
    #   |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
    #   |> yield(name: "mean")'''
    data = filter_data(tStart, tEnd, tInterval, measures, salle)
    data.sort(key=lambda x: x.time)
    return data

def data_for_training(data):
    data_for_training = []
    for i in range(len(data)):
        DFT = {
            'hour': int(data[i].time.strftime('%H')),
            'expected_lux': data[i]._value
        }
        data_for_training.append(DFT)

    return data_for_training

def train_ai_lumiere(data_training, prediction_hour):
    X, y = create_sequences_with_targets(data_training)

    # Model architecture

    model = Sequential()
    model.add(InputLayer((1, 1)))
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
            predicted_lumiere = self.model.predict(np.array([self.input_sequence]), verbose=0)
            print(f"Epoch {epoch + 1} - Predicted Lux: {predicted_lumiere[0, 0]}")
            if epoch + 1 == NUMBER_EPOCHS:
                print(predicted_lumiere)
                LAST_EPOCH_RESULT = predicted_lumiere

    # -------------------------------- A VIRER QUAND LE MODELE MARCHE -------------------------------------
    prediction_hour = int(prediction_hour.strftime('%H'))
    input_sequence_entry = max(np.where(np.array([_x == prediction_hour for _x in X]))[0])
    print(f"NOUS VOULONS PREDIRE :  {y[input_sequence_entry]}")

    input_sequence = np.array(X[input_sequence_entry])
    input_sequence = input_sequence.reshape(1, 1)
    # input_sequence = np.array(input_sequence)
    # input_sequence = input_sequence.reshape(2, PACKET_SIZE)
    # -------------------------------- A VIRER QUAND LE MODELE MARCHE -------------------------------------
    
    # predictions_callback = PredictionsCallback(input_sequence)
    X = X.reshape(len(X), 1)
    predictions_callback = PredictionsCallback(input_sequence)
    model.fit(X, y, epochs=NUMBER_EPOCHS, batch_size=5, verbose=2, callbacks=[predictions_callback])
    model.save(MODEL_PATH)

    return LAST_EPOCH_RESULT

def test_lumiere(prediction_hour):
    tEnd = datetime.utcfromtimestamp(int(prediction_hour)).timestamp()
    tStart = (datetime.utcfromtimestamp(tEnd) - timedelta(hours=PACKET_SIZE)).timestamp()
    data = filter_data(int(tStart), int(tEnd), "1h", ["Luminosité"], "d351_1_multisensor9_illuminance")

    test_ai_lumiere(data_for_training(data, PACKET_SIZE), prediction_hour)
def test_ai_lumiere(data_testing, prediction_hour):
    model = load_model(MODEL_PATH)

    X_test, y_test = create_sequences_with_targets(data_testing)

    prediction_hour = datetime.utcfromtimestamp(int(prediction_hour))
    prediction_hour = int(prediction_hour.strftime('%H'))

    input_sequence = np.array(X_test)
    # input_sequence = input_sequence.reshape(-1, 2, PACKET_SIZE)

    loss = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss}")

    predicted_lumiere = model.predict(np.array(input_sequence), verbose=0)
    return predicted_lumiere[0][0]

def create_sequences_with_targets(data):
    sequences = []
    targets = []
    for entry in data:
        sequences.append((entry['hour']))
        targets.append(entry['expected_lux'])
    return np.array(sequences), np.array(targets)

train_lumiere("1700703993", "1703059200", "1h", ["Luminosité"], "d351_1_multisensor9_illuminance", "1703055600")
# test_lumiere("1703055600")
# predict_lumiere("1700703993", "1703059200", "1h", "µg\/m³", "d351_1_multisensor9_particulate_matter_2_5", "1703059200")

