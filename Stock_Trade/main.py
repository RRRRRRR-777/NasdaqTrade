from utils import *
import time


start = time.time()


# # 初期実行 0.005s
# InitProcess().execute()
# # finvizから銘柄の配列を取得 58.88s 0.98m
# PickFinviz().execute()
# # ヒストリカルデータをダウンロードする 1295.59s 21.59m
# HistData().execute()
# # NASDAQのヒストリカルデータの列を増やす
# ProcessNASDAQ().execute()
# # 個別株のヒストリカルデータの列を増やす 610.45s 10.17m
# ProcessHistData().execute()
# # RSを計算する 91.94s 1.53m
# CalculateRS().execute()
# # BuyingStock.csvを出力する
# BuyingStock().execute()
# # CとAを取得する 2874.17s 47.90m
# CorrentAnnual().execute()
# # 機関投資家の増加数を取得  2345.98s 39.09m
# Institutional().execute()
# # BuyingStock.csvに値を追加する 61.6s → 12s
# AppendData().execute()
# Excelに変換後視覚情報を調整 47.93s(セルの自動調整追加時)
ConvertExcel().execute()


end = time.time()
print(f"All Time : {round(end - start, 2)}")
