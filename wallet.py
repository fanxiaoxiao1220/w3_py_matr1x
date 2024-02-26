import click
from time import sleep
from loguru import logger
from config.eth_wallet import *
from base.metamask import Metamask
from base.utils.dp import get_page_by_adspwer_id
from base.utils.mnemonic import generate_mnemo_12


# 如果是多个命令，这里需要用group
@click.group()
def cli():
    pass


@cli.command(name="gw")
@click.option(
    "-c",
    "--count",
    type=int,
    default=50,
    prompt="请输入生成钱包数量",
    help="生成钱包数量",
)
def generate_wallet(count):
    for index in range(0, count):
        mnemo = generate_mnemo_12()
        print(mnemo)


def _mm_login(ads_id, pwd, w):
    page = get_page_by_adspwer_id(ads_id)
    page.set.window.max()
    page.close_other_tabs()

    Metamask(page).wallet_login(pwd)


def mm_login_by_index(index):
    try:
        # 根据序号查找钱包信息
        wallet = find_wallet_by_index(index)
        if not wallet:
            logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项]")
            return

        ads_id = wallet.get("ads_id")
        pwd = wallet.get("pwd")
        w = wallet.get("w")

        _mm_login(ads_id, pwd, w)
    except Exception as e:
        logger.error(e)


def ph_login_by_index(index):
    # 根据序号查找钱包信息
    wallet = find_wallet_by_index(index)
    if not wallet:
        logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项]")
        return

    ads_id = wallet.get("ads_id")
    pwd = wallet.get("pwd")
    w = wallet.get("w")

    _mm_login(ads_id, pwd, w)


@cli.command("l")
@click.option("-i", "--index", type=int, prompt="请输入浏览器序号", help="浏览器序号")
def mm_login(index):
    mm_login_by_index(index)


@cli.command()
@click.option("-i", "--index", nargs=2, type=int)
def pl(index):
    for index in range(index[0], index[1]):
        try:
            mm_login_by_index(index)
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    cli()
    # get_pks()
