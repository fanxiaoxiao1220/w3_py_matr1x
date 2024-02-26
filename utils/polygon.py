import requests


class Polygon:
    def __init__(self) -> None:
        self.api_key = "MR5QZ18R84T2Q5QI9P382MYYIQBTZKWBVK"

    def txlist(self, eth_address, current_block):
        url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={eth_address}&startblock=0&endblock={current_block}&page=1&offset=20&sort=desc&apikey={self.api_key}"
        resp = requests.get(url).json()
        return resp.get("result")

    # 获取马蹄链的gas接口
    def get_gas(self):
        url = f"https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey={self.api_key}"
        resp = requests.get(url).json()
        return resp
