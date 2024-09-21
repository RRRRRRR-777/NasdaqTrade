from utils import NasdaqHistDownload, ProcessNASDAQ, PlotImage, LineNotify
import os


def main_process(data, context):
    # NASDAQのヒストリカルデータをダウンロード
    data = NasdaqHistDownload()
    # CSVデータに情報を加える
    ProcessNASDAQ(data)
    # Lineに送信する画像の生成
    PlotImage()
    # 売買フラグが立った際にLINEで通知する
    LineNotify()


if __name__ == "__main__":
    main_process()
