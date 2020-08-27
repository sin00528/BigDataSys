import pandas as pd
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor

from xgboost import XGBRegressor
from catboost import CatBoostRegressor

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

import shap
from shap import TreeExplainer

# Font Configuration
matplotlib.rcParams['axes.unicode_minus'] = False
font_name = font_manager.FontProperties(fname="C:/Windows/Fonts/malgun.ttf").get_name()
plt.rc("font", family=font_name)

# Load Data
data = pd.read_excel("./data/HAV_Gwangju.xlsx", encoding="utf-8")

# Train Test Split
X = data.iloc[:, 2:]
y = data["환자"]
X_train = X.iloc[:-5, :]
X_test = X.iloc[-5:, :]
y_train = y[:-5]
y_test = y[-5:]

# Models
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


def auto_learning(m_name, X, y):
    print(m_name.__name__)
    model = m_name().fit(X, y)
    pred = model.predict(X)
    loss = mean_squared_error(y, pred, squared=False)
    print("RMSE: ", loss)
    score_list.append([str(m_name.__name__), round(loss, 2)])


for m_name in model_list:
    auto_learning(m_name, X_train, y_train)


# show models' loss Value
score_df = pd.DataFrame(score_list, columns=["Model", "RMSE"])
print(score_df)

# Draw a graph of Catboost
model = CatBoostRegressor().fit(X_train, y_train, verbose=False)
pred = model.predict(X_test)

num = np.linspace(0, 10, 10)
plt.scatter(y_test, pred)
plt.plot(num)
plt.xlim(-0.1, 1)
plt.ylim(-0.1, 1)
plt.title("CatBoost Prediction")
plt.ylabel('Prediction')
plt.xlabel('Ground Truth')
plt.savefig('./plot/CatBoost_HAV_Gwangju_Scatter.png')
plt.show()
plt.clf()

shap_values = shap.TreeExplainer(model).shap_values(X)
shap.summary_plot(shap_values, X, max_display=10, show=False, plot_size=(15, 5))
plt.subplots_adjust(right=1.1)
plt.savefig('./plot/CatBoost_HAV_Gwangju_Shap.png', format='png')
plt.show()
plt.clf()

"""
# Draw a graph of XGBboost
model = XGBRegressor().fit(X_train, y_train, verbose=False)
pred = model.predict(X_test)

num = np.linspace(0, 10, 10)
plt.scatter(y_test, pred)
plt.plot(num)
plt.xlim(-0.1, 1)
plt.ylim(-0.1, 1)
plt.title("XGBoost Prediction")
plt.ylabel('Prediction')
plt.xlabel('Ground Truth')
plt.savefig('./plot/XGBoost_HAV_Gwangju_Scatter.png')
plt.show()
plt.clf()

shap_values = shap.TreeExplainer(model).shap_values(X)
shap.summary_plot(shap_values, X, max_display=10, show=False, plot_size=(15, 5))
plt.subplots_adjust(right=1.1)
plt.savefig('./plot/XGBoost_HAV_Gwangju_Shap.png', format='png')
plt.show()
plt.clf()
"""