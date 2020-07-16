import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.utils.np_utils import to_categorical

FER2013_PATH = 'data/'
WIDTH = 48
HEIGHT = 48
nClasses = 7

# 데이터 확인
data = pd.read_csv(FER2013_PATH + "fer2013.csv")

# 훈련세트, 검증세트, 테스트세트 나누어서 저장
train_set = data[(data.Usage == 'Training')]
val_set = data[(data.Usage == 'PublicTest')]
test_set = data[(data.Usage == 'PrivateTest')]


# 데이터세트 4차원화
def fer2013_to_X(table):
    X = []
    pixels_list = table["pixels"].values

    for pixels in pixels_list:
        single_image = np.reshape(pixels.split(" "), (WIDTH, HEIGHT)).astype("float")
        X.append(single_image)

    # Convert list to 4D array:
    X = np.expand_dims(np.array(X), -1)

    # Normalize image data:
    X -= np.mean(X, axis=0)
    X /= np.std(X, axis=0)

    # GRAY to RGB
    X = np.squeeze(X)
    X = np.stack((X,) * 3, axis=3)

    return X


# 레이블 추출
def fer2013_to_y(table):
    y = []
    labeled_list = table["emotion"].values
    labeled_list = to_categorical(labeled_list, nClasses)
    y.append(labeled_list)
    y = np.squeeze(y)

    return y


# 변환
train_X = fer2013_to_X(train_set)
val_X = fer2013_to_X(val_set)
test_X = fer2013_to_X(test_set)

train_y = fer2013_to_y(train_set)
val_y = fer2013_to_y(val_set)
test_y = fer2013_to_y(test_set)

# x 형태 출력
print("train_X shape : ", np.shape(train_X))
print("val_X shape : ", np.shape(val_X))
print("test_X shape : ", np.shape(test_X))

# 레이블 형태 출력
print("train_y shape : ", np.shape(train_y))
print("val_y shape : ", np.shape(val_y))
print("test_y shape : ", np.shape(test_y))

# 저장
np.save(FER2013_PATH + "train_X", train_X)
np.save(FER2013_PATH + "val_X", val_X)
np.save(FER2013_PATH + "test_X", test_X)

np.save(FER2013_PATH + "train_y", train_y)
np.save(FER2013_PATH + "val_y", val_y)
np.save(FER2013_PATH + "test_y", test_y)
