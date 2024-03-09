import json
import os
import random, time
from loguru import logger
import okx.Funding as Funding


class OKX:
    def __init__(self) -> None:
        datas = self.read_all_data()
        api_key = datas.get("api_key")
        secret = datas.get("secret")
        passphrase = datas.get("password")
        flag = "0"
        self.funding_api = Funding.FundingAPI(api_key, secret, passphrase, False, flag)

    def config_path(self):
        here = os.path.abspath(os.path.dirname(__file__))
        json_path = os.path.join(here, "./config.json")
        return json_path

    def read_all_data(self):
        json_path = self.config_path()
        with open(json_path, "r") as f:
            datas = json.load(f)
            return datas

    def get_fee(self, token, network):
        currencies = self.funding_api.get_currencies(ccy=token)
        if not currencies:
            logger.error("获取费用失败，请检查你的网络...")
            return

        data = currencies.get("data")
        chain = f"{token}-{network}"
        for item in data:
            _chain = item.get("chain")
            # 判断是否可提现
            canWd = item.get("canWd")
            if chain == _chain:
                if not canWd:
                    logger.error(f"您选择的{_chain}目前不可提现...")
                    continue

                return item.get("minFee")

        return None

    def get_balance(self, token):
        result = self.funding_api.get_balances(token)
        data = result.get("data")
        if not data:
            logger.error("数据获取异常")
            return 0

        for item in data:
            ccy = item.get("ccy")
            if ccy == token:
                return item.get("availBal")

        return 0

    def withdraw(self, address, token, network, amount):
        chain = f"{token}-{network}"
        try:

            balance = self.get_balance(token)
            if float(balance) < float(amount):
                logger.warning(f"{token} 余额不足, 请检余额!")
                return False

            fee = self.get_fee(token, network)
            logger.warning(fee)
            # dest 提币方式 3：内部转账 4：链上提币
            result = self.funding_api.withdrawal(
                ccy=token, amt=amount, dest=4, toAddr=address, fee=fee, chain=chain
            )
            code = result.get("code")
            if int(code) == 0:
                logger.success(
                    f"【{chain}】 Transfer {amount} {token} to {address} succeeded"
                )
                return True

            msg = result.get("msg")
            logger.error(
                f"【{chain}】 Transfer {amount} {token} to {address} failed, error : {msg}"
            )

        except Exception as e:
            logger.error(f"【{chain}】Transfer {amount} ETH to {address} failed: {e}")


def get_amount(start, end):
    count = random.randint(3, 6)
    amount = round(random.uniform(start, end), count)
    return amount


def withdraw():
    address = [
        "0x821315b1C06Ae098dB31Ff3CD5F6AFD5452f144F",
        "0x91b5629C4E66304AB454efD21879276999b0E11D",
    ]

    # token、network 可以通过 self.funding_api.get_currencies 获取查看
    # token 一般为ETH，BTC等

    token = "MATIC"
    network = "Polygon"
    start = 1.1
    end = 2.5
    for addr in address:
        amount = get_amount(start, end)
        logger.info(amount)
        okx = OKX()
        okx.withdraw(address=addr, token=token, network=network, amount=amount)
        time.sleep(random.randint(30, 3600))


if __name__ == "__main__":
    withdraw()
