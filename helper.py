import click
from utils.proxy import check_available_proxies
from utils.create_eth_account import generate_accounts
from fake_useragent import UserAgent
from matr1x.datas import insert_data
from loguru import logger
from base.utils.aes import aes_decrypt, aes_encrypt
from config import AES_KEY


@click.group()
def cli():
    pass


@cli.command("cip")
def check_proxies():
    check_available_proxies()


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
