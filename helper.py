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
        "0xAf5C696d0fd69A538f653B6Bb16d7e06eEFBF687",
        "0xb276e3cDF2196Ff8EBb6CFb5d42b2A6532548E8f",
        "0x1De51F8ae467Ea87c0B5d9EcCA9eC1946a65751C",
        "0x1BF3f8a33675c86E5A69C80D8B5067588c5dD6C8",
        "0x9EAC3988b63B05718145A232328E84272826f8d5",
        "0xd34D2992DFA0121c1F48Ec93fF5B96823dd7Ac6E",
        "0xC25D3d0Eb9c3B46E513a1D9137Bbf84F9f6Fd31e",
        "0x72465173376E172bc8b0e0D1A6069B0AF65969b4",
        "0x453aFacFA48Bd370761562446191E9750C843534",
        "0xdD28C9afe9b7aF82991252a73C4a4C2Ce7f41edD",
        "0x82f3CbE28531A0dF44Ed1Ed13D4ac88087D75541",
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
