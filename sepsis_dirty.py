import pandas as pd
import numpy as np

d = pd.read_csv("ehr_data.csv")
d2 = d.dropna(subset=["x1","x2","x3"])
d2["x4"] = d2["x4"].fillna(d2["x4"].mean())
d2["x5"] = d2["x5"].fillna(0)
d2 = d2[d2["x1"] > 0]
d2 = d2[d2["x2"] < 300]
d2 = d2[d2["x3"] < 50]
d2["z1"] = (d2["x1"] - d2["x1"].mean()) / d2["x1"].std()
d2["z2"] = (d2["x2"] - d2["x2"].mean()) / d2["x2"].std()
d2["z3"] = (d2["x3"] - d2["x3"].mean()) / d2["x3"].std()
d2["z4"] = (d2["x4"] - d2["x4"].mean()) / d2["x4"].std()
d2["z5"] = (d2["x5"] - d2["x5"].mean()) / d2["x5"].std()
d2["y"] = ((d2["x1"] > 38.3) | (d2["x2"] > 90) | (d2["x3"] > 20) | (d2["x4"] > 12)).astype(int)
d3 = d2[["z1","z2","z3","z4","z5","y"]]
d3.to_csv("out.csv", index=False)
print(d3.shape)
print(d3["y"].value_counts())
