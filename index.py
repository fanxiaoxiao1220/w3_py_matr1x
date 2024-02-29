import random, time
import click
from loguru import logger
from fake_useragent import UserAgent
from retry import retry
from config.eth_wallet import *
from base.utils.dp import get_page_by_adspwer_id, get_page_with_browser_name
from base.metamask import Metamask

from matr1x.datas import load_data_list
from matr1x.index import Matr1x
from utils.hhtime import get_current_date
from matr1x.datas import (
    update_registed,
    find_data_by_index,
    update_claimed_date,
    update_last_point,
    update_point,
)


# 如果是多个命令，这里需要用group
@click.group()
def cli():
    pass


def get_pks():
    datas = load_data_list()
    return [data.get("pk") for data in datas if data.get("pk")]


def _claim_key_contact():
    pks = get_pks()
    while pks:
        wallet = random.choice(pks)
        Matr1x(wallet).claim_key()
        pks.remove(wallet)
        time.sleep(random.randint(2, 5))

    logger.success("所有钱包合约执行完成...")


def _get_referral_codes(data):
    index = data.get("index")
    pk = data.get("pk")
    page = _get_page(index, True)
    matr1x = Matr1x(pk)
    codes = matr1x.get_referral_codes(page, index)
    page.close()
    return codes


def write_code2_txt(codes):
    filename = "codes.txt"
    with open(filename, "a") as f:
        for code in codes:
            f.write(f"{code}\n")


@cli.command("codes")
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
def random_get_referral_codes(index):
    data = find_data_by_index(index)
    codes = _get_referral_codes(data)
    write_code2_txt(codes)


# 一次性随机获取邀请码
@cli.command("rc")
def random_get_referral_codes():
    all_codes = []
    datas = load_data_list()
    while datas:
        data = random.choice(datas)
        datas.remove(data)
        try:
            codes = _get_referral_codes(data)
            write_code2_txt(codes)
            all_codes.extend(codes)
        except Exception as e:
            logger.error(e)

    logger.info(all_codes)


# 随机执行合约领取钥匙
@cli.command("rck")
def random_claim_key():
    _claim_key_contact()


# 获取余额，余额不足的打印告警
@cli.command("b")
def banlances():
    pks = get_pks()
    list = []
    for pk in pks:
        matr1x = Matr1x(pk)
        eth_address = matr1x.eth_address
        balance = matr1x.get_balance()
        logger.debug(f"[{eth_address}] 余额为 {balance} matic")
        if balance < 0.5:
            list.append(eth_address)

    logger.info("余额不足0.5的地址有: ")
    logger.info(list)


def _get_page_with_browser_name(index):

    data = find_data_by_index(index)
    page = get_page_with_browser_name(index, data)

    return page


# 获取page，并且通过小狐狸钱包登录
def _get_page(index, need_login=False):

    # 根据序号查找钱包信息
    wallet = find_data_by_index(index)
    if not wallet:
        logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项")
        return

    ads_id = wallet.get("ads_id")
    if ads_id:
        page = get_page_by_adspwer_id(ads_id)
    else:
        page = _get_page_with_browser_name(index)
    page.set.window.max()
    page.close_other_tabs()

    # 导入小狐狸钱包
    if need_login:
        pwd = wallet.get("pwd")
        Metamask(page).wallet_login(pwd)

    return page


# 指定某个需要，指定数量通过合约领取钥匙
@cli.command("claim")
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
@click.option("-c", "--count", type=int, default=4, help="浏览器序号")
def claim(index, count):

    data = find_data_by_index(index)
    pk = data.get("pk")

    matr1x = Matr1x(pk)
    matr1x.claim_key(count, False)


def _register(data):
    url = data.get("url")
    pk = data.get("pk")
    index = data.get("index")

    page = _get_page(index, True)
    mm = Metamask(page)
    network = mm.get_current_network()

    if "Polygon" not in network:
        mm.add_network("Polygon Mainnet")

    matr1x = Matr1x(pk)
    matr1x.register(page, url)

    update_registed(matr1x.eth_address)


@cli.command("ri")
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
def run_item(index):
    data = find_data_by_index(index)
    _run_item(data)


def _run_item(data):
    index = data.get("index")
    pk = data.get("pk")
    page = None
    if not pk:
        logger.warning(f"{index} 获取pk为空, 跳过...")
        return False
    try:
        matr1x = Matr1x(pk)

        # ads_id 为空跳过
        # ads_id = data.get("ads_id")
        # if not ads_id:
        #     logger.warning(f"{index} 获取ads_id为空, 跳过...")
        #     return False

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
        page = _get_page(index, True)
        # 如果claim完成就循环等待钥匙出现
        if result:
            matr1x.wait_key_visible(page, 3)

        point = data.get("point") or 0
        logger.success(f"========== 【{index}】 claim之前的分数为:{point} ==========")
        update_last_point(index=index, last_point=point)

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
                matr1x.wait_key_visible(page, key_count)
            matr1x.claim(page, index)

        # 更新point
        point = matr1x.get_point(page.get_tab(0))
        logger.success(f"========== 【{index}】 claim之后的分数为:{point} ==========")
        # 将信息写入文件
        update_point(index=index, point=point)
        update_claimed_date(index)

    except Exception as e:
        logger.error(e)
    finally:
        if page:
            page.close()


@cli.command("r")
@click.option("-c", "--count", default=4, type=int, help="进程数")
def random_run(count):

    import multiprocessing

    # 创建进程池
    pool = multiprocessing.Pool(processes=count)
    datas = load_data_list()

    async_result = []
    while datas:
        data = random.choice(datas)
        datas.remove(data)

        result = pool.apply_async(_run_item, args=(data,), callback=process_callback)
        async_result.append(result)
        time.sleep(3)

        index = data.get("index")
        print(f"{index} 已经添加到执行队列...")

    for result in async_result:
        result.get()

    # 关闭进程池并等待所有进程完成
    pool.close()
    pool.join()

    logger.info("==========所有的进程都已经跑完==========")


def process_callback(result):
    logger.info(f"{result}任务执行结束")


# 获取唯一邀请码
def get_uni_codes():
    filename = "codes.txt"  # 替换为你的文件名

    # 读取文件内容并去除每行末尾的换行符
    with open(filename, "r") as f:
        lines = f.read().splitlines()

    # 使用 set 进行去重
    unique_lines = set(lines)

    # 输出去重后的结果
    for line in unique_lines:
        print(line)


if __name__ == "__main__":
    cli()
    # logger.info(get_pks())
    # get_uni_codes()
    # banlances()

    # data = find_data_by_index(1000)
    # _run_item(data)
