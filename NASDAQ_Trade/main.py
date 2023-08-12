from utils import NasdaqHistDownload, ProcessNASDAQ, LineNotify


# NASDAQのヒストリカルデータをダウンロード
NasdaqHistDownload()
# CSVデータに情報を加える
ProcessNASDAQ()
# 売買フラグが立った際にLINEで通知する
LineNotify()