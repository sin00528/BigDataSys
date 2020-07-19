# ignore warnings
import warnings
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import numpy as np
import json

import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, KFold

from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, LSTM
from tensorflow.keras.layers import Dropout, GlobalMaxPool1D
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint

np.random.seed(201)

DATA_IN_PATH = './data/word_dict/'
DATA_OUT_PATH = './data_out/'

INPUT_TRAIN_DATA = 'pos_input.npy'
LABEL_TRAIN_DATA = 'pos_label.npy'
DATA_CONFIGS = 'pos_data_configs.json'

input_data = np.load(open(DATA_IN_PATH + INPUT_TRAIN_DATA, 'rb'))
label_data = np.load(open(DATA_IN_PATH + LABEL_TRAIN_DATA, 'rb'))
prepro_configs = json.load(open(DATA_IN_PATH + DATA_CONFIGS, 'r',  -1, "utf-8"))

TEST_SPLIT = 0.2
RND_SEED = 0
VOCAB_SIZE = prepro_configs['vocab_size']+1
EMB_SIZE = 128
BATCH_SIZE = 512
EPOCHS = 5
MAX_LEN = 200
max_features = 20000

"""
train_X, test_X, train_y, test_y = train_test_split(input_data,
                                                    label_data,
                                                    test_size=TEST_SPLIT,
                                                    random_state=RND_SEED)
"""
kf = KFold(n_splits=20, random_state=RND_SEED, shuffle=True)

for train_index, test_index in kf.split(input_data):
    train_X, test_X = input_data[train_index], input_data[test_index]
    train_y, test_y = label_data[train_index], label_data[test_index]


train_X = sequence.pad_sequences(train_X, maxlen=MAX_LEN)
test_X = sequence.pad_sequences(test_X, maxlen=MAX_LEN)

def Model():
    model = Sequential()
    model.add(Embedding(max_features, EMB_SIZE, input_length=MAX_LEN))
    model.add(Bidirectional(LSTM(64, return_sequences=True)))
    model.add(GlobalMaxPool1D())
    model.add(Dropout(0.2))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    return model

model = Model()

model.compile(loss="binary_crossentropy", optimizer='adam', metrics=['accuracy'])
model.summary()

hist = model.fit(train_X, train_y, batch_size=BATCH_SIZE, epochs=EPOCHS)

plt.plot(hist.history['accuracy'])
plt.plot(hist.history['loss'])
plt.legend(['accuracy', 'loss'], loc = 'upper left')
plt.show()

score = model.evaluate(test_X, test_y)
print('Test accuracy: ', score[1])