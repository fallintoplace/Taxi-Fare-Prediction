import tensorflow as tf
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers

from matplotlib import pyplot as plt
from matplotlib import dates as md

column_names = ['fare_amount','pickup_datetime', 'pickup_longitude', 'pickup_latitude',
                'dropoff_longitude', 'dropoff_latitude', 'passenger_count']

"""
PREPARING THE DATASET

"""

def process(file_url):
    dataset = pd.read_csv(file_url)    

    dataset = dataset.dropna()
    dataset = dataset[dataset['dropoff_latitude'] != 0]
    dataset = dataset[dataset['dropoff_longitude'] != 0]
    dataset = dataset[dataset['pickup_latitude'] != 0]
    dataset = dataset[dataset['pickup_longitude'] != 0]
    
    dataset['diff_longtitude'] = dataset.apply(lambda x: 
                    abs(x['pickup_longitude'] - x['dropoff_longitude']), axis=1)
    dataset['diff_latitude'] = dataset.apply(lambda x: 
                    abs(x['pickup_latitude'] - x['dropoff_latitude']), axis=1)
    
    dataset['pickup_datetime'] = [datetime.strptime(x, "%Y-%m-%d %H:%M:%S %Z") 
                                   for x in dataset['pickup_datetime']]
    dataset['hour'] = dataset['pickup_datetime'].apply(lambda x: x.hour)
    dataset['year'] = dataset['pickup_datetime'].apply(lambda x: x.year)
    dataset['day'] = dataset['pickup_datetime'].apply(lambda x: x.dayofyear)
    dataset['weekday'] = dataset['pickup_datetime'].apply(lambda x: x.weekday())
    dataset['week'] = dataset['pickup_datetime'].apply(lambda x: x.week)
    dataset['hour'] = dataset['pickup_datetime'].apply(lambda x: x.hour)
   
    dataset.pop('pickup_datetime')
    return dataset


dataset = process("C:\\Users\\Minh\\Downloads\\new-york-city-taxi-fare-prediction\\train.csv")
dataset = dataset.sample(frac=1).reset_index(drop=True)


train_labels = dataset.pop('fare_amount')
dataset.pop('key')
print(dataset.head())
dataset=(dataset-dataset.mean())/dataset.std()

"""
TWO DENSELY PRELU ACTIVATED CONNECTED LAYERS WITH DROPOUTS, REGULARIZATIONS
AND LAYER NORMALIZATION

"""

def build_model():
    model = keras.Sequential([
        layers.Dense(50, 
                     input_shape = [len(dataset.keys())],
                     kernel_regularizer=regularizers.l1_l2(l1 = 1e-5, l2 = 1e-4),
                     bias_regularizer=regularizers.l2(1e-4),
                     activity_regularizer=regularizers.l2(1e-5)
                     ),
        layers.PReLU(alpha_initializer=tf.initializers.constant(0.25)),
        layers.LayerNormalization(),
        layers.Dropout(rate = 0.5),
        layers.Dense(50, 
                     kernel_regularizer=regularizers.l1_l2(l1 = 1e-5, l2 = 1e-4),
                     bias_regularizer=regularizers.l2(1e-4),
                     activity_regularizer=regularizers.l2(1e-5)
                     ),
        layers.PReLU(alpha_initializer=tf.initializers.constant(0.25)),
        layers.LayerNormalization(),
        layers.Dropout(rate = 0.5),
        layers.Dense(1)
        ])

    model.compile(loss = 'mse',
                optimizer = tf.keras.optimizers.Adam(0.0005),
                )
    return model

model = build_model()
model.summary()


"""
FITTING AND PLOTTING THE LOSS VALUE GRAPH

"""

history = model.fit(
    dataset, train_labels,
    epochs = 1000, batch_size = 128, validation_split = 0.2, verbose = 1,
    callbacks = [keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 20)],
)

plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.legend()
plt.show()

"""
PLOTTING THE PREDICTION GRAPH

"""

test_predictions = model.predict(dataset).flatten()
plt.axes(aspect = 'equal')
plt.scatter(train_labels, test_predictions)
plt.xlabel('True Values')
plt.ylabel('Predictions')
lims = [0, 100]
plt.xlim(lims)
plt.ylim(lims)
plt.plot(lims, lims)

"""
PRINTING THE RESULT

"""


final = process("C:\\Users\\Minh\\Downloads\\new-york-city-taxi-fare-prediction\\test.csv")
final_key = final.pop('key')
final = (final-final.mean())/final.std()
result = pd.DataFrame()
result['key'] = final_key
result['fare_amount']=model.predict(final).flatten()
result['fare_amount']=result['fare_amount'].apply(lambda x: 1 if (x<1) else x)
pd.DataFrame(result).to_csv("C:\\Users\\Minh\\Downloads\\new-york-city-taxi-fare-prediction\\result.csv", index = False)





