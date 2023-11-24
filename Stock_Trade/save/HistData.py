import datetime
import numpy as np
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
import subprocess
import glob
import os
import datetime as dt
import shutil

# from webdriver_manager.chrome import ChromeDriverManager


# ChromeDriverの保存先
chromedriver = r"/Users/yamadariku/chromedriver_mac64/chromedriver"
# 銘柄データの保存先
stocksDir = r"input.txt"
# ダウンロードデータの保存先
dt_now = dt.datetime.now()
date = dt_now.strftime('%y%m%d')
downloadDir = os.getcwd() + r"/CompanyData" + date
try:
    p = glob.glob(os.getcwd() + r"/CompanyData*", recursive=True)[0]
    shutil.rmtree(p)
except:
    pass
os.mkdir(downloadDir)


# 銘柄の箱
symbol = np.full((5000), 0, dtype=object)

# データ期間の指定（st:開始、ed:終了）
st = datetime.date(2021, 1, 1)
ed = datetime.date.today()
dt = datetime.date(1970, 1, 1)
st = st - dt
ed = ed - dt
st = (st.days) * 86400
ed = (ed.days) * 86400

# inputファイルから銘柄群のシンボルを取得
i = 0
if(os.path.exists(stocksDir)):
  with open(stocksDir, 'r', encoding='shift-jis') as f:
    for line in f.readlines():
      i += 1
      toks = line.split('~')
      symbol[i] = toks[0]

# 銘柄数を記録
nsym = i

#ドライバの設定
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_experimental_option("prefs", {"download.default_directory": downloadDir })
chrome_service = fs.Service(executable_path=chromedriver)
driver = webdriver.Chrome(service=chrome_service, chrome_options=options)


# VTのヒストリカルデータをダウンロード
url = 'https://query1.finance.yahoo.com/v7/finance/download/VT?period1='\
        +str(st)+'&period2='+str(ed)+'&interval=1d&events=history&includeAdjustedClose=true'

#日足データのダウンロード
driver.implicitly_wait(30)
driver.get(url)
#2秒間の一時停止
time.sleep(2)

#銘柄数の分だけループ
for i in range(1,nsym+1):
  url = 'https://query1.finance.yahoo.com/v7/finance/download/'+str(symbol[i])+'?period1='\
        +str(st)+'&period2='+str(ed)+'&interval=1d&events=history&includeAdjustedClose=true'

  #日足データのダウンロード
  driver.implicitly_wait(30)
  driver.get(url)
  #2秒間の一時停止
  time.sleep(2)

  if i%10 == 0:
      print(f"{str(symbol[i])} {int(i)}/{int(nsym)}")
