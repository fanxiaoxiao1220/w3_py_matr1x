import click, random
from utils.proxy import check_available_proxies
from utils.create_eth_account import generate_accounts
from fake_useragent import UserAgent
from matr1x.datas import insert_data
from loguru import logger
from base.utils.aes import aes_decrypt, aes_encrypt
from config import AES_KEY
from base.okx import get_amount, OKX
from time import sleep


@click.group()
def cli():
    pass


@cli.command("cip")
def check_proxies():
    check_available_proxies()


@cli.command("okx")
def okx_withdraw():
    address = [
        "0x87dE9ce13fe6B61e6CdD9E032fb1793341cDE244",
    ]

    # token、network 可以通过 okx.funding_api.get_currencies 获取查看
    # token 一般为ETH，BTC等

    token = "MATIC"
    network = "Polygon"
    start = 1.1
    end = 2.5
    for addr in address:
        amount = get_amount(start, end)
        okx = OKX()
        okx.withdraw(address=addr, token=token, network=network, amount=amount)
        sleep(random.randint(30, 120))


def _generate_data(count, password):
    logger.info(f"正在生成 {count} 条数据...")

    accounts = generate_accounts(count)
    for account in accounts:
        pk = account[0]
        w = account[1]
        eth_address = account[2]
        ua = UserAgent(os=["windows", "macos"]).chrome

        insert_data(eth_address, w, pk, password, ua)

    logger.success(f"正在生成 {count} 条数据完成")


# 批量生成数据
@cli.command("gd")
@click.option("-c", "--count", type=int, default=100, help="生成的数据条数")
@click.option("-p", "--password", type=str, default="abc12345", help="小狐狸钱包密码")
def generate_data(count, password):
    _generate_data(count, password)


if __name__ == "__main__":
    cli()
