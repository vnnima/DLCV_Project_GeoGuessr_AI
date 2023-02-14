import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.stats import t
import statsmodels.api as sm
import pygeohash as phg

# get the performance csv
df = pd.read_csv(dir+"\\finalpretrainedresnet50_performance.csv", delimiter=',', skiprows=0, low_memory=False)
# get the coordinates csv of all training data
ds = pd.read_csv(dir+"\\coordinates.csv", delimiter=',', skiprows=0, low_memory=False)

# add geohash to ds and df
ds['geohash']=ds.apply(lambda coords: phg.encode(coords.latitude, coords.longitude, precision=3), axis=1)
df["geohash"] = df.apply(lambda coords: phg.encode(coords.actual_lat, coords.actual_lon, precision=3), axis=1)

# for every geohash in df get the number of samples with same geohash in ds
df["num_samples"] = df.apply(lambda row: ds["geohash"].value_counts().get(row.geohash, 0), axis=1)

# declare X and y
X = df[["num_samples"]]
y = df["round_score_points"]

# pefom linear regression
model = LinearRegression()
model.fit(X, y)

# get analysis
X2 = sm.add_constant(X)
est = sm.OLS(y, X2)
est2 = est.fit()
print(est2.summary())