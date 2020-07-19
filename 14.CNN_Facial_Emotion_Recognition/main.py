# ignore warnings
import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import numpy as np
import matplotlib.pyplot as plt

import tensorflow
from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras.preprocessing.image import ImageDataGenerator

FER2013_DIR = "data/"
INPUT_TRAIN_DATA = 'fer2013_X.npy'
LABEL_TRAIN_DATA = 'fer2013_y.npy'

np.random.seed(201)
RND_SEED = 0
BATCH_SIZE = 32
EPOCHS = 200

# 데이터 로드
train_X = np.load(open(FER2013_DIR + 'train_X.npy', 'rb'))
val_X = np.load(open(FER2013_DIR + 'val_X.npy', 'rb'))
test_X = np.load(open(FER2013_DIR + 'test_X.npy', 'rb'))

train_y = np.load(open(FER2013_DIR + 'train_y.npy', 'rb'))
val_y = np.load(open(FER2013_DIR + 'val_y.npy', 'rb'))
test_y = np.load(open(FER2013_DIR + 'test_y.npy', 'rb'))


# x 형태 출력
print("train_X shape : ", np.shape(train_X))
print("val_X shape : ", np.shape(val_X))
print("test_X shape : ", np.shape(test_X))

# 레이블 형태 출력
print("train_y shape : ", np.shape(train_y))
print("val_y shape : ", np.shape(val_y))
print("test_y shape : ", np.shape(test_y))

# CNN 모델 정의
base_model = ResNet50(weights=None, include_top=False, input_shape=(48, 48, 3))
x = base_model.output
x = Flatten()(x)
predictions = Dense(7, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.summary()

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

check_point = ModelCheckpoint(filepath='./logs/weights', monitor='val_accuracy', verbose=1, save_best_only=True)
tensor_board = TensorBoard(log_dir='./logs', histogram_freq=1, embeddings_freq=1)

# Data Agementation
datagen = ImageDataGenerator(featurewise_center=True,
                             featurewise_std_normalization=True,
                             rotation_range=20,
                             width_shift_range=0.2,
                             height_shift_range=0.2,
                             horizontal_flip=True)
datagen.fit(train_X)

# 실시간 데이터 증강을 사용해 배치에 대해서 모델을 학습합니다:
history = model.fit_generator(datagen.flow(train_X, train_y, batch_size=BATCH_SIZE),
                              validation_data=(val_X, val_y),
                              steps_per_epoch=len(train_X) / BATCH_SIZE,
                              epochs=EPOCHS,
                              callbacks=[check_point, tensor_board])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Training for ' + str(EPOCHS) + ' epochs')
plt.legend(['Training accuracy', 'Validation accuracy'], loc='lower right')
plt.show()

results = model.evaluate(test_X, test_y)
print('Test accuracy: ', results[1])