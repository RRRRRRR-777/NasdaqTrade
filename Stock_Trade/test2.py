import os
from selenium import webdriver
import time
import pandas as pd
import numpy as np
import glob


df_dir = glob.glob(os.getcwd()+"/Stock_Trade/Comprehensive.csv")[0]
df = pd.read_csv(df_dir)["Ticker"]
ticker_list = df.to_list()

data = [[ticker, np.nan] for ticker in ticker_list]

print(data)