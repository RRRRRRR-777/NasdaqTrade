#moduleをインポート
import datetime
import glob
import numpy as np
import os
import pandas as pd
import re
import requests
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
import shutil
import subprocess
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import glob
import yfinance as yf
import yahoo_fin.stock_info as si
import math
import sys
import seaborn as sns
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from matplotlib.colors import Normalize, to_rgba, ListedColormap, colorConverter
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib


from matplotlib.colors import TwoSlopeNorm
norm = TwoSlopeNorm( vcenter=0.0, vmin=-20.0, vmax=100.0)



# ! Volume SMA50 Gap