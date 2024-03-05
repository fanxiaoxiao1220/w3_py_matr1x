import random, time
import json
from web3 import Web3, HTTPProvider
from eth_account import Account
from retry import retry
from loguru import logger
from config.abi_config import nft_abi
from config import POLYGON_RPC, SHOULD_WAIT_FOR_TASK_COMPLETION
from utils.hhtime import is_same_day
from utils.polygon import Polygon
from base.metamask import Metamask


rpc = POLYGON_RPC
contrac_address = "0x0f3284bFEbc5f55B849c8CF792D39cC0f729e0BC"
chainId = 137


class ConnectXException(Exception):
    def __init__(self, message="twitter授权异常"):
        super().__init__(message)


class Matr1x:
    def __init__(self, pk) -> None:
        self.w3 = Web3(HTTPProvider(rpc))
        self.contract = self.w3.eth.contract(address=contrac_address, abi=nft_abi)
        account = Account.from_key(pk)
        self.pk = pk
        self.eth_address = account.address
        self.connect_x = False
        self.task_count = 0  # 验证任务数

    def _claim_key_with_contract(self):
        try:
            txn = self.contract.functions.claimKey().build_transaction(
                {
                    "gas": random.randint(110000, 120000),
                    "gasPrice": int(self.w3.eth.gas_price * 1.1),
                    "nonce": self.w3.eth.get_transaction_count(self.eth_address),
                }
            )

            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.pk)
            order_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            transaction_receipt = self.w3.eth.wait_for_transaction_receipt(order_hash)
            if transaction_receipt.status == 1:
                logger.success(f"{self.eth_address} claimKey成功")
                return True
        except Exception as e:
            logger.error(f"{self.eth_address} claimKey失败! {e}")

        return False

    def get_point(self, tab):
        eles = tab.eles("x://div[@class='value']")
        if len(eles) >= 3:
            point = eles[2].text.strip()
        else:
            logger.warning("获取point异常")
            point = "-1"
        return point

    def _open_key(self, last_tab, index):
        # 打开盒子
        while True:
            open = last_tab.ele("x://span[text()='Open ']/parent::button")
            disabled = open.attr("disabled")
            if not open or disabled == "disabled":
                logger.success(f"[{index}] claim 结束...")
                break
            open.click()

            # 关闭弹窗
            time.sleep(0.5)
            ele = last_tab.ele("x://span[text()=' ok ']/parent::button")
            if ele:
                ele.click()

            time.sleep(random.randint(1, 3))

    # 链接钱包
    def _connect_wallet(self, last_tab):
        # 判断是否已链接钱包
        ele = last_tab.ele("x://span[text()=' Connect Wallet ']", timeout=3)
        if ele:
            ele.click()
            # 点击metamask按钮
            last_tab.ele("x://div[text()=' MetaMask ']").click()

    # claim 其他
    def _claim_task(self, last_tab):
        eles = last_tab.eles("x://span[text()=' CLAIM ']/parent::button")
        for ele in eles:
            ele.click()
            time.sleep(1)
            # 关闭弹窗
            try:
                last_tab.ele("x://span[text()=' ok ']/parent::button").click()
            except Exception as e:
                logger.error(e)
            time.sleep(1)

    # 检测当前是否有claim key
    # 目前检测3次，如果要操作超过3次，认为是已经操作过啦
    def _check_claimed(self):
        # 获取当前区块高度
        current_block = self.w3.eth.block_number

        try:
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
        except Exception as e:
            logger.error(e)

        return False

    # 获取钱包余额
    def get_balance(self):
        balance = 0
        try:
            _balance = self.w3.eth.get_balance(self.eth_address)
            balance = self.w3.from_wei(_balance, "ether")
        except Exception as e:
            logger.error(e)
        return balance

    def register(self, page, invite_code):
        last_tab = page.get_tab(0)
        url = f"https://matr1x.io/max-event?ic={invite_code}"
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
        ele = last_tab.ele("x://span[text()=' Activate ']/parent::button", timeout=5)
        if ele:
            ele.click()
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

    # 等待钥匙出现
    @retry(tries=3, delay=1)
    def wait_key_visible(self, page, key_count=0):
        last_tab = page.get_tab(0)
        while True:
            last_tab.get("https://matr1x.io/max-event")
            logger.info(f"已经打开的钥匙 {key_count}")
            count = self.get_unpack_key_count(page)
            if count >= key_count:
                logger.info(f"{self.eth_address} 出现钥匙, 继续执行任务...")
                break

            time.sleep(10)

    # 领取积分
    @retry(tries=3, delay=1)
    def claim(self, page, index):
        last_tab = page.get_tab(0)
        last_tab.get("https://matr1x.io/max-event")
        time.sleep(5)

        # 链接钱包
        self._connect_wallet(last_tab)

        self._open_key(last_tab, index)
        # claim任务
        self._claim_task(last_tab)

    # 获取claim过未打开的钥匙数量
    def get_unpack_key_count(self, page):
        # 查询是否还有钥匙
        last_tab = page.get_tab(0)
        time.sleep(3)
        ele = last_tab.ele("Key Count:").next()
        key_count = int(ele.text)
        logger.info(f"[{self.eth_address}] 待打开钥匙 {key_count}个")
        return key_count

    # 获取钥匙数量
    def get_key_count(self, page):
        # 查询是否还有钥匙
        last_tab = page.get_tab(0)
        key = last_tab.ele("Keys to be collected:").next()
        key_count = int(key.text)
        if key_count > 0:
            logger.info(f"[{self.eth_address}] 还可以领取{key.text}个钥匙")

        return key_count

    def _get_connect_x_button(self, page):
        last_tab = page.get_tab(0)
        eles = last_tab.eles(
            "x://div[@class='pointsTaskListWarp']//button[@class='el-button btn el-button--default']"
        )
        for ele in eles:
            title = ele.parent(2).ele(".taskContent").child(1).text
            if (
                "Open Case" in title
                or "Refer Friends" in title
                or "Join MATR1X" in title
            ):
                continue

            connect_x_ele = last_tab.ele(
                "x://span[text()=' Connect Twitter ']/parent::button", timeout=3
            )
            return connect_x_ele

    # 关联x
    @retry(ConnectXException, tries=5, delay=3)
    def connectx(self, page, index):

        last_tab = page.get_tab(0)
        last_tab.get("https://matr1x.io/max-event")

        # 判断是否要链接twitter
        if self.connect_x:
            logger.success(f"{index} 已经关联过twitter, 无需重复关联")
            return

        connect_x_ele = self._get_connect_x_button(page)
        if not connect_x_ele:
            self.connect_x = True
            logger.success(f"{index} 已经关联过twitter, 无需重复关联")
            return

        logger.info(f"{index} 准备关联twitter账号")
        self.connect_x = False
        page.listen.start("https://api.matr1x.io/matr1x-points/task/authTwitter")
        connect_x_ele.click()

        page.wait.ele_loaded("@data-testid=OAuth_Consent_Button")
        last_tab.ele("@data-testid=OAuth_Consent_Button").click()

        for packet in page.listen.steps():
            response = packet.response
            body = json.loads(response.raw_body)
            code = body.get("code")
            if code != 0:
                logger.warning(response)
                self.connect_x = False
                raise ConnectXException()
            else:
                logger.success("x 授权成功")
                self.connect_x = True
            break

    # 完成任务
    @retry(tries=5, delay=1)
    def task(self, page, index):
        # logger.info(f"{index} 准备开始执行任务...")
        last_tab = page.get_tab(0)
        last_tab.get("https://matr1x.io/max-event")

        self.connectx(page, index)

        self.task_count = 0
        # 查找未完成的任务，然后去执行
        eles = last_tab.eles(
            "x://div[@class='pointsTaskListWarp']//button[@class='el-button btn el-button--default']"
        )
        for ele in eles:
            title = ele.parent(2).ele(".taskContent").child(1).text
            if (
                "Open Case" in title
                or "Refer Friends" in title
                or "Join MATR1X" in title
            ):
                continue

            ele.click()
            time.sleep(2)
            ele = last_tab.ele(".downloadModel", timeout=3)
            if not ele:
                logger.warning(f"{title} 点击后弹窗未出现....")
                continue

            ele = last_tab.ele(
                "x://span[text()=' VERIFYING ']/parent::button", timeout=2
            )
            if ele:
                logger.warning("已经验证过, 正在等待任务...")
                last_tab.ele("x://div[@class='close']").click()
                continue

            try:
                last_tab.ele(
                    "x://span[text()=' VERIFY ']/parent::button", timeout=3
                ).click()
                self.task_count += 1
                time.sleep(3)
            except Exception as e:
                logger.error(e)

        if self.task_count > 0 and SHOULD_WAIT_FOR_TASK_COMPLETION == 1:
            time.sleep(120)

        logger.success(f"{index} 所有任务执行完成...")

    def claim_key(self, count=3, is_check=True):
        balance = self.get_balance()
        eth_address = self.eth_address
        if balance == 0:
            logger.warning(f"{self.eth_address} 余额为0, 请检查...")
            return False

        logger.info(f"[{eth_address}] 余额为 {balance} matic")

        # 检查今日是否已经claim
        is_claimed = self._check_claimed()
        if is_claimed and is_check:
            logger.warning(
                f"[{eth_address}] 今日已经claim超过3次, 无需重复执行, 本次跳过"
            )
            return False

        for _ in range(count):
            self._claim_key_with_contract()
            time.sleep(random.randint(2, 5))

        return True

    def get_referral_codes(self, page, index):
        last_tab = page.get_tab(0)
        last_tab.get("https://matr1x.io/max-event")
        time.sleep(3)

        page.listen.start("https://api.matr1x.io/matr1x-points/referral/overview")
        last_tab.ele("x://p[@class='invite']").click()

        codes = []
        for packet in page.listen.steps():

            response = packet.response
            body = json.loads(response.raw_body)
            code = body.get("code")
            if code != 0:
                return codes

            data = body.get("data")
            taskCodes = data.get("taskCodes")
            for task in taskCodes:
                state = task.get("state")
                inviteCode = task.get("inviteCode")
                if state == 1:
                    codes.append(inviteCode)

            logger.info(f"{index} code 有:{codes}")
            return codes
