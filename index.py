import random, time
import click
from loguru import logger
from retry import retry
from config.eth_wallet import *
from base.utils.dp import get_page_by_adspwer_id
from base.metamask import Metamask
from matr1x.datas import load_data_list
from matr1x.index import Matr1x
from utils.hhtime import get_current_date
from matr1x.datas import update_registed, find_data_by_index, update_claimed_date


# 如果是多个命令，这里需要用group
@click.group()
def cli():
    pass


def get_wallets():
    file_path = "config/bera_private_keys_hh_1000.txt"
    wallets = []
    with open(file_path, "r") as file:
        count = 0
        for private_key in file:
            private_key_str = private_key.strip()
            count += 1
            wallets.append(private_key_str)

    return wallets


@cli.command()
def main():
    wallets = get_wallets()
    # wallets = ["0x98662865f16a191ec04e32f939f88d3fa2219941ccfac41d12fd761c18cfae63"]

    while wallets:
        wallet = random.choice(wallets)
        Matr1x(wallet).claim_key()
        wallets.remove(wallet)
        time.sleep(random.randint(2, 5))

    logger.success("所有钱包合约执行完成...")


@cli.command("b")
def banlances():
    wallets = get_wallets()
    list = []
    for pk in wallets:
        matr1x = Matr1x(pk)
        eth_address = matr1x.eth_address
        balance = matr1x.get_balance()
        if balance < 0.5:
            logger.warning(f"[{eth_address}] 余额为不足 0.5 matic")
            list.append(eth_address)

    logger.info(list)


def _get_page(index, ads_id, need_login=False):

    # 根据序号查找钱包信息
    wallet = find_wallet_by_index(index)
    if not wallet:
        logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项")
        return

    ads_id = wallet.get("ads_id")

    # 打开指纹浏览器，并关闭其他窗口
    page = get_page_by_adspwer_id(ads_id)
    page.set.window.max()
    page.close_other_tabs()

    # 导入小狐狸钱包
    if need_login:
        pwd = wallet.get("pwd")
        Metamask(page).wallet_login(pwd)

    return page


@cli.command()
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
def claim(index):

    data = find_data_by_index(index)
    pk = data.get("pk")

    matr1x = Matr1x(pk)
    matr1x.claim_key(4, False)


def _register(data):
    url = data.get("url")
    pk = data.get("pk")
    index = data.get("index")
    ads_id = data.get("ads_id")

    page = _get_page(index, ads_id, True)
    mm = Metamask(page)
    network = mm.get_current_network()

    if "Polygon" not in network:
        mm.add_network("Polygon Mainnet")

    matr1x = Matr1x(pk)
    matr1x.register(page, url)
    matr1x.connect_twitter(page)

    update_registed(matr1x.eth_address)


@cli.command("ri")
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
def run_item(index):
    data = find_data_by_index(index)
    _run_item(data)


def _run_item(data):
    index = data.get("index")
    pk = data.get("pk")
    if not pk:
        logger.warning(f"{index} 获取pk为空, 跳过...")
        return False

    matr1x = Matr1x(pk)

    # ads_id 为空跳过
    ads_id = data.get("ads_id")
    if not ads_id:
        logger.warning(f"{index} 获取ads_id为空, 跳过...")
        return False

    # 当天执行过不再执行
    claimed_date = data.get("claimed_date")
    current_date = get_current_date()
    if claimed_date == current_date:
        logger.warning(f"[{index}]当天已经执行过，跳过...")
        return False

    # 余额检查
    balance = matr1x.get_balance()
    eth_address = matr1x.eth_address
    if balance == 0:
        logger.warning(f"{eth_address} 余额为0, 请充值...")
        return False

    # 未注册先注册
    registed = data.get("registed")
    if not registed:
        logger.warning(f"{index} 还未注册, 进行注册...")
        _register(data)

    address = data.get("address")
    logger.info(f"准备执行【{index}】号浏览器, 钱包地址：【{address}】")

    # 通过合约进行claim
    result = matr1x.claim_key()
    page = _get_page(index, ads_id, True)
    # 如果claim完成就循环等待钥匙出现
    if result:
        matr1x.wait_key_visible(page)

    # 完成任务, 领取积分
    for _ in range(3):
        matr1x.claim(page, index)
        try:
            matr1x.task(page, index)
        except Exception as e:
            logger.error(e)

    key_count = matr1x.get_key_count(page)
    if key_count > 0:
        result = matr1x.claim_key(key_count, False)
        # 如果claim完成就循环等待钥匙出现
        if result:
            matr1x.wait_key_visible(page)
        matr1x.claim(page, index)

    update_claimed_date(index)

    page.close()


@cli.command("r")
def random_run():

    datas = load_data_list()
    while datas:
        data = random.choice(datas)
        try:
            result = _run_item(data)
            if not result:
                datas.remove(data)
                continue
        except Exception as e:
            logger.error(e)

        datas.remove(data)
        time.sleep(random.randint(1, 3))

    logger.success("所有任务执行完成...")


if __name__ == "__main__":
    # cli()
    data = find_data_by_index(48)
    _run_item(data)
