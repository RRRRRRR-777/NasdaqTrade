import os
import traceback

from dotenv import load_dotenv
from logrelay.line_relay import LineRelay
from utils import LineNotify, NasdaqHistDownload, PlotImage, ProcessNASDAQ

if __name__ == "__main__":
    # LogRelayの初期化
    load_dotenv
    line_relay = LineRelay(
        line_access_token=os.getenv("LINE_MESSAGEING_LOG_RELAY_TOKEN"),
        user_id=os.getenv("LINE_USER_ID"),
    )
    try:
        # NASDAQのヒストリカルデータをダウンロード
        data = NasdaqHistDownload()
        # CSVデータに情報を加える
        ProcessNASDAQ(data)
        # Lineに送信する画像の生成
        PlotImage()
        # 売買フラグが立った際にLINEで通知する
        LineNotify()
    except Exception as e:
        line_relay.send_message("NasdaqTradeでエラーが発生しました")
        line_relay.send_message(f"エラーが発生しました\nNot Exitst ^IXIC.csv: {str(e)}")
        line_relay.send_message(f"トレースバック: {traceback.format_exc()}")
        print(
            f"エラーが発生しました\nNot Exitst ^IXIC.csv: {str(e)}\nトレースバック: {traceback.format_exc()}")
