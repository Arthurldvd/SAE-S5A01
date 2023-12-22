from datetime import datetime

import numpy as np
import tensorflow as tf
from keras.src.callbacks import Callback
from keras.src.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from influxdb_service import request_influxBD, init_influxdb



def predict_temperature():
    init_influxdb()
    #1 retourner un object comme dans IA.py (projet externe)
    #2 train le modèle avec une requête qui récupère TOUTES les températures de toutes les heures
    #3 prédire une heure en précisant l'heure, la prédiction se fera sur les x heures précedentes qui
    # ont du sens
    #4 filtrer la requete sur une seule salle
    data = get_training_data()
    train_ai(data)

def get_training_data():
    request = '''
    from(bucket: "IUT_BUCKET")
      |> range(start: 1700703993, stop: 1703172412)
      |> filter(fn: (r) => r["_measurement"] == "°C")
      |> filter(fn: (r) => r["_field"] == "value")
      |> filter(fn: (r) => r["domain"] == "sensor")
      |> filter(fn: (r) => r["entity_id"] == "d251_1_co2_air_temperature")
      |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
      |> yield(name: "mean")'''
    data = request_influxBD(request)
    data.sort(key=lambda x: x._time)
    return data

def train_ai(data):
    # Extracting features from data
    time_data = [datetime.timestamp(d._time) for d in data]
    temperature_data = [d._value for d in data]
    presence_data = [True for _ in data]

    # Creating datatable using numpy
    datatable = np.column_stack((time_data, temperature_data, presence_data))

    # Creating sequences for training
    seq_length = 3
    X, y = create_sequences_with_presence(datatable, seq_length)

    # Model architecture
    model = Sequential()
    model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(seq_length, 3),kernel_initializer='glorot_uniform'))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(1))
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse')

    # Predicting for the next hour using the latest available data
    latest_time = time_data[-1]
    latest_presence = presence_data[-1]
    latest_temperature = temperature_data[-1]

    class PredictionsCallback(Callback):
        def __init__(self, input_sequence):
            self.input_sequence = input_sequence

        def on_epoch_end(self, epoch, logs=None):
            predicted_temperature = self.model.predict(self.input_sequence, verbose=0)
            print(f"Epoch {epoch + 1} - Predicted Temperature: {predicted_temperature[0, 0]}")

    # Training the model with the callback
    input_sequence = np.array([time_data[-3:], temperature_data[-3:], presence_data[-3:]]).T
    input_sequence = input_sequence.reshape((1, seq_length, 3))

    predictions_callback = PredictionsCallback(input_sequence)
    model.fit(X, y, epochs=100, batch_size=4, verbose=2, callbacks=[predictions_callback])

def create_sequences_with_presence(data, seq_length):
    sequences = []
    target = []
    for i in range(len(data) - seq_length):
        seq = data[i:i + seq_length]
        label = data[i + seq_length, 1]  # Temperature is the second column
        sequences.append(seq)
        target.append(label)
    return np.array(sequences), np.array(target)

def cross_table(time_data, temperature_data, presence_data, length):
    datatable = np.column_stack((time_data, temperature_data, presence_data))
    return datatable

predict_temperature()

