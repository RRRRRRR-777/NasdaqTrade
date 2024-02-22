from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from bs4 import BeautifulSoup
import shutil
import selenium
import pandas as pd
import time
import glob
import numpy as np
import sys
import re


# 関数の定義
# 機関投資家数のパフォーマンスを取得する関数
def get_inst_perf(i, ticker):
    if '-' in ticker:
        ticker = ticker.replace('-', '.')
    try:
        # サイトのホームへ移動
        driver.get("https://whalewisdom.com")
        # 各銘柄のページへ移動
        input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div/header/div/div[2]/div[1]/div[2]/div/div/div/div[2]/input[1]")
        input_search.clear()
        input_search.send_keys(ticker)
        input_search.send_keys(Keys.ENTER) # エンターキーを押下
        tmp_ticker = ticker + " " # 銘柄の検索に空白が必要なので一時的に空白を追加
        xpath_expression = f"//td[text()='{tmp_ticker}']/preceding-sibling::td/a"
        ticker_btn = driver.find_element(By.XPATH, xpath_expression)
        ticker_btn.click()
        # ページソースを収録
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "summary_div"))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        # 目的の要素を取得する
        try:
            perf_inst = soup.find(id="summary_div").find_all("tr")[2].find("span").text
            try:
                get_ticker = soup.find(class_="profile-default").find("h1").find("a").text
                true_or_false = ticker == get_ticker
            except:
                true_or_false = np.nan
                print("cound not be earned True or False")
        except Exception as e:
            perf_inst = np.nan
            true_or_false = np.nan
            if add_error_flg == True:
                error_data.append(ticker)
            print(f"{i+1} | {ticker} Value could not be earned \n {e}")
            print("-------------------------------------------------------------------------------------------------------------------")
    except Exception as e:
        try:
            # 該当銘柄の企業名で再度検索する
            driver.get("https://whalewisdom.com")
            input_search = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div/header/div/div[2]/div[1]/div[2]/div/div/div/div[2]/input[1]")
            input_search.clear()
            company = stock_df[stock_df["Ticker"]==ticker]["Company"].to_string(index=False)
            input_search.send_keys(company)
            input_search.send_keys(Keys.ENTER) # エンターキーを押下
            xpath_expression = f"//td[text()='{tmp_ticker}']/preceding-sibling::td/a"
            driver.find_element(By.XPATH, xpath_expression).click()
            # ページソースを収録
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "summary_div"))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            # 目的の要素を取得する
            try:
                perf_inst = soup.find(id="summary_div").select("span")[2].text
                try:
                    get_ticker = soup.find(class_="profile-default").find("h1").find("a").text
                    true_or_false = ticker == get_ticker
                except:
                    true_or_false = np.nan
                    print("cound not be earned True or False")
            except Exception as e:
                perf_inst = np.nan
                true_or_false = np.nan
                if add_error_flg == True:
                    error_data.append(ticker)
                print(f"{i+1} | {ticker} Value could not be earned \n {e}")
                print("-------------------------------------------------------------------------------------------------------------------")
        except:
            perf_inst = np.nan
            true_or_false = np.nan
            if add_error_flg == True:
                error_data.append(ticker)
            print(f"{i+1} | {ticker} Value could not be earned (Error) \n {e}")
            print("-------------------------------------------------------------------------------------------------------------------")

    if add_error_flg == True:
        data.append([ticker, perf_inst, true_or_false])
    else:
        # 既存の要素を上書き
        for item in data:
            if item[0] == ticker:
                item[1] = perf_inst
                item[2] = true_or_false
def execute():
    # 銘柄のリストを読み込む
    stock_df = pd.read_csv(os.getcwd()+"/Stock_Trade/BuyingStock.csv")
    stock_df_ticker = stock_df["Ticker"]
    # リスト型のデータ変数
    global data
    data  = []
    global error_data
    error_data = []
    # エラーが起こった際に再実行するためのリストに追加するフラグ
    global add_error_flg
    add_error_flg = True

    # 対象リンク
    loggin_url = "https://whalewisdom.com/login"
    # ユーザーネーム
    username = os.getenv("whalewisdom_username")
    # パスワード
    password = os.getenv("whalewisdom_password")
    # WEBブラウザの起動
    chromedriver = os.getcwd() + "/driver/chromedriver"
    #ドライバの設定
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36')
    options.add_argument('--user-data-dir=~/Library/Application Support/Google/Chrome')
    options.add_argument('--profile-directory=Profile1')
    global driver
    driver = webdriver.Chrome(chromedriver, options=options)
    driver.set_window_size(1200, 1000)
    # 暗黙的な待機
    driver.implicitly_wait(30)

    # txtファイルを用いて処理の実行を100銘柄づつに分ける
    remove_flg = False
    process_txt_file = os.getcwd()+"/Stock_Trade/Institutional.txt"
    is_file = os.path.isfile(process_txt_file)

    if is_file: # ファイルが存在する場合の処理
        f = open(process_txt_file, 'r')
        start_num = int(f.read())+100
        if start_num+100 <= len(stock_df_ticker):
            end_num = start_num+100
        else:
            end_num = len(stock_df_ticker)
            remove_flg = True
    else: # ファイルが存在しない場合の処理
        if 100 <= len(stock_df_ticker):
            start_num = 0
            end_num = 100
        else:
            start_num = 0
            end_num = len(stock_df_ticker)
            remove_flg = True
    # ファイルの書き込み
    f = open(process_txt_file, 'w')
    f.write(f"{start_num}")
    f.close()
    # ファイルの削除
    if remove_flg:
        os.remove(process_txt_file)

    # サイトにログインする
    driver.get(loggin_url) # URLを開く
    time.sleep(0.5)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "lnk-login"))) # ページ上の指定の要素が読み込まれるまで待機（15秒でタイムアウト判定）
    driver.find_element(By.ID, "lnk-login").click()
    input_login = driver.find_element(By.ID, "login")
    input_login.clear()
    input_login.send_keys(username)
    input_pass = driver.find_element(By.ID, "password")
    input_pass.clear()
    input_pass.send_keys(password)
    driver.find_element(By.CLASS_NAME, "login").click()
    time.sleep(5) # 待機時間
    driver.get("https://whalewisdom.com") # URLを開く
    time.sleep(0.5)
    # 検索をStock Onlyに変更
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[1]/div/header/div/div[2]/div[1]/div[1]/div/div/div/div[1]/div[1]/div").click()
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[4]/div/div").click()
    print(driver.current_url)

    for i, ticker in enumerate(stock_df_ticker[start_num:end_num]):
        # 値の取得
        get_inst_perf(i, ticker)
        print(f"{i+start_num+1}/{end_num} ", end="\r")
        time.sleep(1.0) # 待機時間

    # errorになった銘柄のデータを再度取得する
    if len(error_data) != 0:
        print("error_data process")
        time.sleep(15) # 待機時間
        add_error_flg = False
        print(error_data)
        # errorになった銘柄のデータを再度取得する
        for i, ticker in enumerate(error_data):
            get_inst_perf(i, ticker)
            print(f"{i+start_num+1}/{len(error_data)} ", end="\r")
            time.sleep(1.0) # 待機時間

    # dataをdfに変換する
    df = pd.DataFrame(data)
    col = ["Ticker", "Perf Inst", "True or False"]
    df.columns = col

    # dfを出力する
    outputDir = os.path.join(glob.glob(os.getcwd()+"/Stock_Trade")[0], f"Perf_Inst_{start_num}.csv")
    df.to_csv(outputDir, index=False)

    # Chrome driverを終了する
    driver.quit()

def Institutional():
    #実行時間の計測
    start = time.time()
    # ファイルが存在しない場合の初回実行
    execute()
    # ファイルが削除されるまで処理を繰り返す
    while os.path.isfile(os.getcwd() + "/Stock_Trade/Institutional.txt"):
        execute()

    df_dict = {}
    df_dir_ = glob.glob(os.getcwd()+"/Stock_Trade/Perf_Inst_*.csv")
    df_dir = sorted(df_dir_, key=lambda x: int(re.search(r'\d+', x).group())) # 数値部分を抽出してソート

    # CSVファイルを読み込んでデータフレームに結合
    dfs = [pd.read_csv(file) for file in df_dir]
    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df.to_csv(os.getcwd()+"/Stock_Trade/Perf_Inst.csv", index=False)

    # ファイルを削除
    for file in df_dir:
        os.remove(file)

    print(f"Time : {round(time.time() - start, 2)}")

# 処理の実行
Institutional()
