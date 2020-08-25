#%%
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error

from xgboost import XGBRegressor
from catboost import CatBoostRegressor


#%%

data = pd.read_excel("./data/HAV_TimeSeq.xlsx", encoding="utf-8")
data.drop(["날짜"], axis='columns', inplace=True)
data.head()

#%%
# Data Normalization
scaler = MinMaxScaler()
data = pd.get_dummies(data)
scaler.fit(data)
sc = scaler.transform(data)
col = data.columns
sc = pd.DataFrame(sc, columns=col)

#%%
# Train Test Split
y = sc["환자"]
X = sc.iloc[:, 1:]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2)
X_train.shape, X_test.shape, y_train.shape, y_test.shape

#%%

model_list = [RandomForestRegressor,
              GradientBoostingRegressor,
              Lasso,
              Ridge,
              LinearRegression,
              KNeighborsRegressor,
              MLPRegressor,
              XGBRegressor,
              CatBoostRegressor]

score_list = []

#%%
for m_name in model_list:
    model = m_name().fit(X, y)
    pred = model.predict(X)
    loss = mean_squared_error(y, pred, squared=False)
    score_list.append([str(m_name.__name__), round(loss, 2)])

#%%
# show models' loss Value
score_df = pd.DataFrame(score_list, columns=["Model", "RMSE"])
print(score_df)
