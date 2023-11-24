import requests
from requests_html import HTMLSession
import numpy as np
import glob
import os


ticker = np.full((5000),0,dtype=object)
company = np.full((5000),0,dtype=object)
sector = np.full((5000),0,dtype=object)
industry = np.full((5000),0,dtype=object)
mcap = np.full((5000),0,dtype=object)
per = np.full((5000),0,dtype=object)
fper = np.full((5000),0,dtype=object)
price = np.full((5000),0,dtype=object)
volume = np.full((5000),0,dtype=object)
edate = np.full((5000),0,dtype=object)


print("START")

cnt = 0
#ページが開けなかった場合に備えて10回ループ
while cnt < 10:
  cnt += 1
  #URL読み込み
  load_url = 'https://finviz.com/screener.ashx?v=111&f=geo_usa&o=-marketcap,\
              ind_stocksonly&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'
  #html読み込み
  session = HTMLSession()
  r = session.get(load_url)
  #htmlが正常に読み込めたら以下に入る
  if r.status_code >= 200 and r.status_code < 300:
    #tdタブ区切りのデータのみ読み込む
    article = r.html.find("td")
    #tdタブ区切りのデータ1つ1つを確認
    for item_html in article:
      #tdタブ区切りのデータに"Page"と入った物があれば、ページ数を表すデータ
      if item_html.text[:4] == "Page":
        #”Page 1/96"の"96"だけが欲しいので、"/"でデータを区切って"/"の後ろのデータだけ取る
        tmp = item_html.text.split('/')
        tmp = tmp[1].splitlines()
        np = int(tmp[0])
        # print(np)
        #データが取れたのでループ処理を抜ける
        break
    break

j = 0
#ページ数だけループ
# np=5 # 上位100銘柄
np=50 # 上位1000銘柄
print(np*20)
for i in range(1,np+1):
  cnt = 0
  dflg = 0
  dcnt = 0
  n1 = 0
  n2 = 0
  n3 = 0
  n4 = 0
  n5 = 0
  n6 = 0
  n7 = 0
  n8 = 0
  n9 = 0
  n10 = 0
  while cnt < 10:
    cnt += 1
    #URL読み込み（urlに(ページNo.-1)*20+1が入る）
    load_url = 'https://finviz.com/screener.ashx?v=152&f=cap_smallover,exch_nasd,\
                ind_stocksonly&o=-marketcap&r='+str(1+(i-1)*20)+'&c=0,1,2,3,4,6,7,8,65,67,68'
    session = HTMLSession()
    r = session.get(load_url)
    if r.status_code >= 200 and r.status_code < 300:
      article = r.html.find("td")
      for item_html in article:
        dcnt = dcnt+1
        #”Eanings"の次から基本情報データが始まる
        if item_html.text == str("Earnings") and j == (i-1)*20:
          dflg = 1
          #No.（読まない）,Ticker,Company,Sector, Industry, Market Cap.,PER,Forward PER,
          #Price, Volume, Earnings Dateの順にデータが並んでいる
          n1 = dcnt+2
          n2 = dcnt+3
          n3 = dcnt+4
          n4 = dcnt+5
          n5 = dcnt+6
          n6 = dcnt+7
          n7 = dcnt+8
          n8 = dcnt+9
          n9 = dcnt+10
          n10 = dcnt+11
        if dcnt == n1 and dflg == 1:
          j += 1
          ticker[j] = item_html.text
          #データはNo.を入れて11個あるので、11個先が次のデータ
          n1 = dcnt+11
        elif dcnt == n2 and dflg == 1:
          company[j] = item_html.text
          n2 = dcnt+11
        elif dcnt == n3 and dflg == 1:
          sector[j] = item_html.text
          n3 = dcnt+11
        elif dcnt == n4 and dflg == 1:
          industry[j] = item_html.text
          n4 = dcnt+11
        elif dcnt == n5 and dflg == 1:
          mcap[j] = item_html.text
          n5 = dcnt+11
        elif dcnt == n6 and dflg == 1:
          per[j] = item_html.text
          n6 = dcnt+11
        elif dcnt == n7 and dflg == 1:
          fper[j] = item_html.text
          n7 = dcnt+11
        elif dcnt == n8 and dflg == 1:
          price[j]= dcnt+11
        elif dcnt == n9 and dflg == 1:
          volume[j] = item_html.text
          n9 = dcnt+11
        elif dcnt == n10 and dflg == 1:
          edate[j] = item_html.text
          n10 = dcnt+11
          #1ページに表示される銘柄は20個なので、20個読んだら次のページに行く
          if j == 20+(i-1)*20:
            break
    break
#最後にどうしても1つ無駄なデータを読んでしまうので-1する
# ndata = j-1
ndata = j

#書き込むファイルのアドレスを指定
write_dir = os.path.join(glob.glob(os.getcwd()+r"/Stock_Trade/StockData*", recursive=True)[0], 'input.txt')
with open(r"input.txt", 'w', encoding='shift-jis') as f:
  #データ数だけループ
  for i in range(1,ndata+1):
    #データ書き込み（社名にカンマが入っている場合があるので"~"区切り）
    f.write(str(ticker[i])+'~'+str(company[i])+'~'+str(sector[i])+'~'+str(industry[i])+
            '~'+str(mcap[i])+'~'+str(per[i])+'~'+str(fper[i])+'~'+str(price[i])+
            '~'+str(volume[i])+'~'+str(edate[i])+'\n')

"""
finvizから銘柄の配列を取得
"""
def PickFinviz():
    file = os.path.join(glob.glob(os.getcwd()+r"/Stock_Trade/StockData*", recursive=True)[0], 'input.txt')

    ticker = np.full((5000),0,dtype=object)
    company = np.full((5000),0,dtype=object)
    sector = np.full((5000),0,dtype=object)
    industry = np.full((5000),0,dtype=object)
    mcap = np.full((5000),0,dtype=object)
    per = np.full((5000),0,dtype=object)
    fper = np.full((5000),0,dtype=object)
    price = np.full((5000),0,dtype=object)
    volume = np.full((5000),0,dtype=object)
    edate = np.full((5000),0,dtype=object)

    cnt = 0
    #ページが開けなかった場合に備えて10回ループ
    while cnt < 10:
        cnt += 1
        #URL読み込み
        load_url = 'https://finviz.com/screener.ashx?v=111&f=geo_usa&o=-marketcap,\
                    ind_stocksonly&o=-marketcap&c=0,1,2,3,4,6,7,8,65,67,68'
        #html読み込み
        session = HTMLSession()
        r = session.get(load_url)
        #htmlが正常に読み込めたら以下に入る
        if r.status_code >= 200 and r.status_code < 300:
            #tdタブ区切りのデータのみ読み込む
            article = r.html.find("td")
            #tdタブ区切りのデータ1つ1つを確認
            for item_html in article:
            #tdタブ区切りのデータに"Page"と入った物があれば、ページ数を表すデータ
                if item_html.text[:4] == "Page":
                    #”Page 1/96"の"96"だけが欲しいので、"/"でデータを区切って"/"の後ろのデータだけ取る
                    tmp = item_html.text.split('/')
                    tmp = tmp[1].splitlines()
                    num = int(tmp[0])
                    #データが取れたのでループ処理を抜ける
                    break
                break

    j = 0
    #ページ数だけループ
    # num=5 # 上位100銘柄
    # num=50 # 上位1000銘柄
    num=1
    print(f"Pick Stocks are {num*20}")
    for i in range(1,num+1):
        cnt = 0
        dflg = 0
        dcnt = 0
        n1 = 0
        n2 = 0
        n3 = 0
        n4 = 0
        n5 = 0
        n6 = 0
        n7 = 0
        n8 = 0
        n9 = 0
        n10 = 0
        while cnt < 10:
            cnt += 1
            #URL読み込み（urlに(ページNo.-1)*20+1が入る）
            load_url = 'https://finviz.com/screener.ashx?v=152&f=cap_smallover,exch_nasd,\
                        ind_stocksonly&o=-marketcap&r='+str(1+(i-1)*20)+'&c=0,1,2,3,4,6,7,8,65,67,68'
            session = HTMLSession()
            r = session.get(load_url)
            if r.status_code >= 200 and r.status_code < 300:
                article = r.html.find("td")
                for item_html in article:
                    dcnt = dcnt+1
                    #”Eanings"の次から基本情報データが始まる
                    if item_html.text == str("Earnings") and j == (i-1)*20:
                        dflg = 1
                        #No.（読まない）,Ticker,Company,Sector, Industry, Market Cap.,PER,Forward PER,
                        #Price, Volume, Earnings Dateの順にデータが並んでいる
                        n1 = dcnt+2
                        n2 = dcnt+3
                        n3 = dcnt+4
                        n4 = dcnt+5
                        n5 = dcnt+6
                        n6 = dcnt+7
                        n7 = dcnt+8
                        n8 = dcnt+9
                        n9 = dcnt+10
                        n10 = dcnt+11
                    if dcnt == n1 and dflg == 1:
                        j += 1
                        ticker[j] = item_html.text
                        #データはNo.を入れて11個あるので、11個先が次のデータ
                        n1 = dcnt+11
                    elif dcnt == n2 and dflg == 1:
                        company[j] = item_html.text
                        n2 = dcnt+11
                    elif dcnt == n3 and dflg == 1:
                        sector[j] = item_html.text
                        n3 = dcnt+11
                    elif dcnt == n4 and dflg == 1:
                        industry[j] = item_html.text
                        n4 = dcnt+11
                    elif dcnt == n5 and dflg == 1:
                        mcap[j] = item_html.text
                        n5 = dcnt+11
                    elif dcnt == n6 and dflg == 1:
                        per[j] = item_html.text
                        n6 = dcnt+11
                    elif dcnt == n7 and dflg == 1:
                        fper[j] = item_html.text
                        n7 = dcnt+11
                    elif dcnt == n8 and dflg == 1:
                        price[j]= dcnt+11
                    elif dcnt == n9 and dflg == 1:
                        volume[j] = item_html.text
                        n9 = dcnt+11
                    elif dcnt == n10 and dflg == 1:
                        edate[j] = item_html.text
                        n10 = dcnt+11
                    #1ページに表示される銘柄は20個なので、20個読んだら次のページに行く
                        if j == 20+(i-1)*20:
                            break
                break
    #最後にどうしても1つ無駄なデータを読んでしまうので-1する
    # ndata = j-1
    ndata = j

    #書き込むファイルのアドレスを指定
    with open(file, 'w', encoding='shift-jis') as f:
        #データ数だけループ
        for i in range(1,ndata+1):
            #データ書き込み（社名にカンマが入っている場合があるので"~"区切り）
            f.write(str(ticker[i])+'~'+str(company[i])+'~'+str(sector[i])+'~'+str(industry[i])+
                    '~'+str(mcap[i])+'~'+str(per[i])+'~'+str(fper[i])+'~'+str(price[i])+
                    '~'+str(volume[i])+'~'+str(edate[i])+'\n')

    print(f"---Done Write input.txt (PickFinviz)---")
