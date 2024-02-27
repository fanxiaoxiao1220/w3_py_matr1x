import requests
import config


class Polygon:
    def __init__(self) -> None:
        self.api_key = config.POLYGON_API_KEY
        if not self.api_key:
            raise Exception("还未配置polygon api key")

    def txlist(self, eth_address, current_block):
        url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={eth_address}&startblock=0&endblock={current_block}&page=1&offset=20&sort=desc&apikey={self.api_key}"
        resp = requests.get(url).json()
        return resp.get("result")

    # 获取马蹄链的gas接口
    def get_gas(self):
        url = f"https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey={self.api_key}"
        resp = requests.get(url).json()
        return resp
