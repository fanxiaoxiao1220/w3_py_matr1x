from loguru import logger
from retry import retry
from config import METAMASK_EXTENSION_PATH
from time import sleep


class LoadException(Exception):
    def __init__(self, message="打开页面异常"):
        super().__init__(message)


def check_metamask_page(func):
    def wrapper(self, *args, **kwargs):
        last_tab = self.page.get_tab(0)
        if "MetaMask" not in last_tab.title:
            logger.warning("当前页面不是钱包页面, 请确认...")
            return
        return func(self, *args, **kwargs)

    return wrapper


class Metamask:
    def __init__(self, page):
        self.page = page

    # 首次导入助记词
    def _import_account(self, phrase, password):
        logger.info(" ========== 开始导入助记词 ========== ")

        # ========== 同意导入协议 ==========
        sleep(1)
        self.page.ele("#onboarding__terms-checkbox").click()
        self.page.ele("x://button[@data-testid='onboarding-import-wallet']").click()
        self.page.ele("x://button[@data-testid='metametrics-i-agree']").click()

        # ========== 导入助记词 ==========
        w = phrase.split(" ")
        word_len = len(w)

        # 如果是24个长度助记词，切换成24
        if word_len == 24:
            ele = self.page.ele(
                "x://div[@class='dropdown import-srp__number-of-words-dropdown']//select"
            )
            ele.select.by_value("24")

        for index in range(len(w)):
            item = f"#import-srp__srp-word-{str(index)}"
            word = w[index]
            self.page.ele(item).input(word)
            sleep(0.2)

        self.page.ele("x://button[@data-testid='import-srp-confirm']").click()
        sleep(1)

        # ========== 设置密码 ==========
        logger.info("开始设置密码...")
        eles = self.page.eles(".form-field__input")
        eles[0].input(password)
        eles[1].input(password)
        self.page.ele(".check-box far fa-square").click()
        self.page.ele("x://button[@data-testid='create-password-import']").click()

        # 点击完成
        sleep(6)
        self.page.ele("x://button[@data-testid='onboarding-complete-done']").click()
        self.page.ele("x://button[@data-testid='pin-extension-next']").click()
        self.page.ele("x://button[@data-testid='pin-extension-done']").click()

        sleep(6)
        logger.info(f"准备关闭pop页...")
        self.page.ele('x://button[@data-testid="popover-close"]').click()

        ele = self.page.ele(".whats-new-popup__notifications")
        if ele:
            self.page.ele('x://button[@data-testid="popover-close"]', timeout=3).click()

        logger.info(" ========== 结束导入助记词 ========== ")

    def wallet_setup(self, phrase: str, password: str):
        self.password = password

        # 开始访问插件
        # logger.info(f"准备访问{METAMASK_EXTENSION_PATH}")
        self.page.get(METAMASK_EXTENSION_PATH)
        self.page.close_other_tabs()

        ele = self.page.ele(
            "x://input[@data-testid='onboarding-terms-checkbox']", timeout=3
        )
        if ele:
            self._import_account(phrase, password)
            return

        # 如果有pop页面，需要先关闭
        ele = self.page.ele(".whats-new-popup__notifications", timeout=6)
        if ele:
            self.page.ele('x://button[@data-testid="popover-close"]').click()
            sleep(1)

        # 查找导入token按钮
        ele = self.page.ele('x://button[@data-testid="import-token-button"]', timeout=3)
        if ele:
            logger.info("已经导入过数据, 并且已经登录完成")
            return

        # 输入密码
        self.wallet_login(password)

    def wallet_login(self, password: str):
        # 开始访问插件
        # logger.info(f"准备访问{METAMASK_EXTENSION_PATH}")
        self.page.get(METAMASK_EXTENSION_PATH)

        ele = self.page.ele(".whats-new-popup__notifications", timeout=6)
        if ele:
            self.page.ele('x://button[@data-testid="popover-close"]', timeout=3).click()

        # 查找导入token按钮
        ele = self.page.ele('x://button[@data-testid="import-token-button"]', timeout=3)
        if ele:
            logger.info("已经导入过数据, 并且已经登录完成")
            return

        # 输入密码
        ele = self.page.ele("#password", timeout=3)
        if not ele:
            logger.info("已经登录过, 无需重复登录")
            return
        ele.input(password)
        self.page.ele('x://button[@data-testid="unlock-submit"]').click()

    def try_add_network(self):
        logger.info("正在准备添加网络...")

    def get_current_network(self):
        last_tab = self.page.get_tab(0)
        last_tab.get(METAMASK_EXTENSION_PATH)

        ele = last_tab.ele(
            "x://button[@data-testid='network-display']/span[1]", timeout=3
        )
        return ele.text

    # 添加常用网络
    def add_network(self, name):
        logger.info(f"准备添加{name}网络...")

        last_tab = self.page.get_tab(0)
        url = f"{METAMASK_EXTENSION_PATH}#settings/networks/add-popular-custom-network"
        last_tab.get(url)
        ele = last_tab.ele(
            f"x://h6[text()='{name}']/parent::div/parent::div/following-sibling::*/button",
            timeout=5,
        )
        if not ele:
            logger.warning("输入的网络有误或者已经添加过...")
            return
        ele.click()

        sleep(2)
        last_tab.ele("x://button[@data-testid='confirmation-submit-button']").click(
            "js"
        )

        # 点击切换网络
        sleep(2)
        last_tab.ele(
            ".button btn--rounded btn-primary home__new-network-added__switch-to-button",
            timeout=5,
        ).click()

    # 链接登录
    @check_metamask_page
    def connect(self):
        logger.info("准备开始连接metamask...")
        try:
            last_tab = self.page.get_tab(0)
            last_tab.ele("x://button[@data-testid='page-container-footer-next']").click(
                "js"
            )
            last_tab.ele("x://button[@data-testid='page-container-footer-next']").click(
                "js"
            )

            sleep(3)
            self.page.wait.new_tab()
            last_tab = self.page.get_tab(0)
            # 如果是签名，则点击签名按钮
            ele = last_tab.ele(".request-signature__notice", timeout=6)
            if not ele:
                logger.warning("未找到签名元素...")
                return

            logger.info("执行签名操作...")
            last_tab = self.page.get_tab(0)
            last_tab.ele("x://button[@data-testid='page-container-footer-next']").click(
                "js"
            )
        except Exception as e:
            logger.error(e)

    # 同意切换网络
    def approve_change_network(self):
        logger.info("同意切换网络...")

    def change_network(self, target_network):
        logger.info(f"开始切换网络{target_network}...")

        # # 开始访问插件
        # logger.info(f"准备访问{METAMASK_EXTENSION_PATH}")
        # driver.open_new_window(METAMASK_EXTENSION_PATH)
        # time.sleep(1)
        # driver.switch_last_window()

        # ele = driver.try_find('//button[@data-testid="network-display"]')
        # if ele is None:
        #     logger.error("当前页面异常, 请检查")
        #     return

        # logger.info("点击切换网络按钮")
        # driver.try_click('//button[@data-testid="network-display"]', 1)

        # ele = driver.try_find(f'//div[@data-original-title="{target_network}"]')
        # ele1 = driver.try_find(f'//span[text()="{target_network}"]/parent::button')
        # if ele is None and ele1 is None:
        #     logger.error(f"未找到{target_network}网络")
        #     return

        # if ele:
        #     ele.click()
        # elif ele1:
        #     ele1.click()

        # logger.info(f"完成切换网络{target_network}...")
        # time.sleep(3)
        # driver.close()
        # driver.switch_last_window()

    # 同意授权
    def approve(self):
        logger.info("开始同意授权...")
        last_tab = self.page.get_tab(0)
        last_tab.ele("x://button[@data-testid='page-container-footer-next']").click(
            "js"
        )

    # 同意金额授权
    def approve_amount(self):
        logger.info("开始同意金额授权...")
        # driver.switch_last_window()

        # # 点击最大金额按钮
        # driver.try_click(
        #     "//input[@type='text']/parent::*/parent::*/following-sibling::div[1]/button",
        #     1,
        # )
        # driver.try_click("//footer/button[2]", 1)
        # driver.try_click("//footer/button[2]", 1)

    # 拒绝授权
    def reject(self):
        pass

    # 获得钱包地址
    def get_address(self):
        pass
