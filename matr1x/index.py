import requests, random, time
from web3 import Web3, HTTPProvider
from eth_account import Account
from retry import retry
from loguru import logger
from config.abi_config import nft_abi
from utils.time_utils import is_same_day
from utils.polygon import Polygon
from base.metamask import Metamask
from matr1x.datas import update_point, update_registed

rpc = "https://polygon-mainnet.infura.io/v3/9559c1dc84ca4a87a9ebad7d7b7da7a2"
contrac_address = "0x0f3284bFEbc5f55B849c8CF792D39cC0f729e0BC"
chainId = 137


class Matr1x:
    def __init__(self, pk) -> None:
        self.w3 = Web3(HTTPProvider(rpc))
        self.contract = self.w3.eth.contract(address=contrac_address, abi=nft_abi)
        account = Account.from_key(pk)
        self.pk = pk
        self.eth_address = account.address
        self.connect_x = False

    def claim_key(self):
        balance = self.get_balance()
        eth_address = self.eth_address
        if balance == 0:
            logger.warning(f"{self.eth_address} 余额为0, 请检查...")
            return False

        logger.info(f"[{eth_address}] 余额为 {balance} matic")

        # 检查今日是否已经claim
        is_claimed = self.check_claimed()
        if is_claimed:
            logger.warning(
                f"[{eth_address}] 今日已经claim超过3次, 无需重复执行, 本次跳过"
            )
            return False

        for _ in range(3):
            self._claim_key_with_contract()
            time.sleep(random.randint(2, 5))

        return True

    @retry(tries=3, delay=1)
    def _claim_key_with_contract(self):
        txn = self.contract.functions.claimKey().build_transaction(
            {
                "gas": random.randint(110000, 120000),
                "gasPrice": int(self.w3.eth.gas_price * 1.01),
                "nonce": self.w3.eth.get_transaction_count(self.eth_address),
            }
        )

        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.pk)
        order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        transaction_receipt = self.w3.eth.wait_for_transaction_receipt(order_hash)
        if transaction_receipt.status == 1:
            logger.success(f"{self.eth_address} claimKey成功")
            return True

        logger.error(f"{self.eth_address} claimKey失败!")
        return False

    def _get_point(self, tab):
        eles = tab.eles("x://div[@class='value']")
        point = eles[2].text
        return point.strip()

    # 获取钱包余额
    def get_balance(self):
        _balance = self.w3.eth.get_balance(self.eth_address)
        balance = self.w3.from_wei(_balance, "ether")
        return balance

    # 检测当前是否有claim key
    # 目前检测3次，如果要操作超过3次，认为是已经操作过啦
    def check_claimed(self):
        # 获取当前区块高度
        current_block = self.w3.eth.block_number

        results = Polygon().txlist(self.eth_address, current_block)
        # logger.info(results)
        claimKey_calls = 0
        for tx in results:
            timestamp = tx.get("timeStamp")
            func = tx.get("functionName")
            if "claimKey()" in func and is_same_day(int(timestamp)):
                claimKey_calls += 1

            if claimKey_calls >= 3:
                return True

        return False

    def register(self, page, url):
        last_tab = page.get_tab(0)
        last_tab.get(url)

        # 点击加入
        ele = last_tab.ele(
            "x://span[text()=' Join MAX Score Airdrop ']/parent::button", timeout=5
        )
        if ele:
            ele.click()

        # 判断是否已链接钱包
        mm = Metamask(page)
        ele = last_tab.ele("x://span[text()=' Connect Wallet ']", timeout=5)
        if ele:
            ele.click()
            # 点击metamask按钮
            last_tab.ele("x://div[text()=' MetaMask ']").click()

            page.wait.new_tab()
            mm.connect()

        # 激活
        last_tab.ele("x://span[text()=' Activate ']/parent::button", timeout=5).click()
        last_tab.ele("x://span[text()=' CHECK ']/parent::button", timeout=5).click()
        last_tab.ele("x://span[text()=' CLAIM ']/parent::button").click()

        page.wait.new_tab()
        time.sleep(3)
        mm.approve()

        # 检查是否激活完成
        while True:
            time.sleep(3)
            last_tab.get(url)
            ele = last_tab.ele("x://p[text()=' Invite Friends to Boost ']")
            if ele:
                break

        logger.success(f" {self.eth_address} 激活完成...")

    # 领取积分
    def claim(self, page, index):
        last_tab = page.get_tab(0)
        point = self._get_point(last_tab)
        if point == "--":
            logger.warning("网络未加载成功...")
            raise Exception("页面网络获取失败，重新加载...")

        logger.success(f"========== 【{index}】 claim之前的分数为:{point} ==========")

        # 判断是否已链接钱包
        ele = last_tab.ele("x://span[text()=' Connect Wallet ']", timeout=5)
        if ele:
            ele.click()

            # 点击metamask按钮
            last_tab.ele("x://div[text()=' MetaMask ']").click()

        # 打开盒子
        while True:
            open = last_tab.ele("x://span[text()='Open ']/parent::button")
            disabled = open.attr("disabled")
            if not open or disabled == "disabled":
                logger.info(f"[{index}]claim结束...")
                break

            open.click()

            # 关闭弹窗
            try:
                time.sleep(0.5)
                last_tab.ele("x://span[text()=' ok ']/parent::button").click()
            except Exception as e:
                logger.error(e)

            time.sleep(random.randint(1, 3))

        # claim 其他
        eles = last_tab.eles("x://span[text()=' CLAIM ']/parent::button")
        for ele in eles:
            ele.click()
            # 关闭弹窗
            try:
                time.sleep(1)
                last_tab.ele("x://span[text()=' ok ']/parent::button").click()
            except Exception as e:
                logger.error(e)

        point1 = self._get_point(last_tab)

        logger.success(f"========== 【{index}】 claim之后的分数为:{point1} ==========")

        # 查询是否还有钥匙
        key = last_tab.ele("Keys to be collected:").next()
        key_count = 0
        if int(key.text) > 0:
            logger.error(f"[{index}] 还可以领取{key.text}个钥匙")
            key_count = key.text

        # 将信息写入文件
        update_point(index=index, point=point1, last_point=point, key_count=key_count)

    # 完成任务
    def task(self, page, index):
        last_tab = page.get_tab(0)
        last_tab.get("https://matr1x.io/max-event")

        # 查找未完成的任务，然后去执行
        eles = last_tab.eles(
            "x://div[@class='pointsTaskListWarp']//button[@class='el-button btn el-button--default']"
        )
        for ele in eles:
            title = ele.text
            # 如果是go按钮，就跳过不执行
            if "Go" in title:
                continue

            ele.click()
            time.sleep(2)
            ele = last_tab.ele(
                "x://span[text()=' VERIFYING ']/parent::button", timeout=5
            )
            if ele:
                logger.warning("已经验证过, 正在等待任务...")
                last_tab.ele("x://div[@class='close']").click()
                continue

            # 判断是否需要链接twitter
            ele = last_tab.ele(
                "x://span[text()=' Connect X ']/parent::button", timeout=5
            )
            if ele and not self.connect_x:
                ele.click()
                page.wait.ele_loaded("@data-testid=OAuth_Consent_Button")
                last_tab.ele("@data-testid=OAuth_Consent_Button").click()
                time.sleep(5)
                self.connect_x = True
                self.task(page, index)

            last_tab.ele("x://span[text()=' VERIFY ']/parent::button").click()

        logger.success(f"{index}所有任务执行完成...")
