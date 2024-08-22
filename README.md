## 概要
### Nasdaqのチャートをスクレイピング
※ NasDaq: ナスダックはアメリカに2つある株式市場の1つで、取引する立会場がない電子取引所として1971年に創設
  
その情報をもとに分析し Date, Adj Close, Performance, Volume, U/D, Totalの値とチャート情報を画像にして出力
 - Date: 日付
 - Adj Close: [終値](https://www.jpx.co.jp/glossary/a/48.html#:~:text=%E7%B5%82%E5%80%A4(%E3%81%8A%E3%82%8F%E3%82%8A%E3%81%AD),%E3%81%A8%E5%91%BC%E3%82%93%E3%81%A7%E3%81%84%E3%81%BE%E3%81%99%E3%80%82)(1日のうちで、最後に取引された値段)
 - Performance: 前日との変化率(%)
 - Volume: [出来高](https://www.smbcnikko.co.jp/terms/japan/te/J0055.html#:~:text=%E3%82%84%E3%81%99%E3%81%84%E7%94%A8%E8%AA%9E%E9%9B%86-,%E5%87%BA%E6%9D%A5%E9%AB%98%E3%80%80%EF%BC%88%E3%81%A7%E3%81%8D%E3%81%A0%E3%81%8B%EF%BC%89,-%E5%87%BA%E6%9D%A5%E9%AB%98%E3%81%A8%E3%81%AF)出来高とは、期間中に成立した売買の数量のこと
 - U/D: UpDownVolumeRatio([株価が上昇した日の出来高を合計し、その合計を株価が下落した日の出来高で割って計算します。株価が上昇した日の出来高は、買い誘導によるものであり、株価は積み上がっている、という前提である。逆に、その日の終値が値下がりしている銘柄は、売買が売りを誘発していると判断され、分配のサインとなる。上下の出来高比率が1.0より大きいと強気、1.0より小さいと弱気とみなされる。](https://www.marketedge.com/MarketEdge/DRME/drUDRatio.aspx#:~:text=The%20Up/Down,regarded%20as%20Bearish.))
 - Total: [下記の7つの指標を満たしているトータルの数](https://investortat.com/apply_trend_template_for_japanese_stocks/#:~:text=%E3%81%8C%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82-,%E3%83%88%E3%83%AC%E3%83%B3%E3%83%89%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88%E3%81%AE%E6%9D%A1%E4%BB%B6,-%E3%83%88%E3%83%AC%E3%83%B3%E3%83%89%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88%E3%81%AE)
   1. 現在の株価が150日(30週)と200日(40週)の移動平均線を上回っている。
   2. 150日移動平均線は200日移動平均線を上回っている。
   3. 200日移動平均線は少なくとも1ヶ月上昇トレンドにある。
   4. 50日(10週)移動平均線は150日移動平均線と200日移動平均線を上回っている。
   5. 現在の株価は50日移動平均線を上回っている。
   6. 現在の株価は52週安値よりも、少なくとも30％高い。
   7. 現在の株価は52週高値から少なくとも25％以内にある。
      
その画像をGoogleCloudFunctionにデプロイし、LineNotifyを用いてLineに通知を送信する

これを毎日午前9時にcron実行するようにしている

## 出力画像
![522532301322584118](https://github.com/user-attachments/assets/603a9fc8-c19c-41ea-9b12-79ac145f354c)
