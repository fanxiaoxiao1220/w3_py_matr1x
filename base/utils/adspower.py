import requests
from retry import retry


class OpenErrorException(Exception):
    def __init__(self, message="打开浏览器异常，重试"):
        super().__init__(message)


@retry(OpenErrorException, tries=3, delay=1)
def get_address_with_adspower(aid):
    debugger_address = None
    try:
        url = "http://127.0.0.1:50325/api/v1/browser/start?user_id=" + aid
        resp = requests.get(url).json()

        if resp["code"] != 0:
            print(resp["msg"])
            print("please check ads_id")
            raise OpenErrorException()

        debugger_address = resp["data"]["ws"]["selenium"]
    except Exception as e:
        raise OpenErrorException()

    return debugger_address


def close_browser_with_adspower_id(aid):
    close_url = "http://127.0.0.1:50325/api/v1/browser/stop?user_id=" + aid
    requests.get(close_url)
