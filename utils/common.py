from base.utils.dp import get_page_by_adspwer_id
from loguru import logger
from config.eth_wallet import *
from datetime import datetime, timezone


def get_page(index):
    # 根据序号查找钱包信息
    wallet = find_wallet_by_index(index)
    if not wallet:
        logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项]")
        return None

    ads_id = wallet.get("ads_id")

    # 打开指纹浏览器，并关闭其他窗口
    return get_page_by_adspwer_id(ads_id)


def get_current_date():
    current_utc = datetime.utcnow()
    return current_utc.strftime("%Y-%m-%d")


def get_date_from_timestamp(timestamp):
    dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)
    return dt_utc.strftime("%Y-%m-%d")


def is_same_day(timestamp):
    date = get_date_from_timestamp(timestamp)
    current_data = get_current_date()
    return date == current_data
