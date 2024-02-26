import os
from base.utils.excel import Excel
from base.utils.aes import aes_decrypt, aes_encrypt
from config import AES_KEY
from loguru import logger

wallet_list = None


# 获得基础信息
def wallet_info_from_excel():
    _path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "eth_wallet.xlsx")
    return Excel(_path).readAllData()


def load_wallet_list():
    global wallet_list
    if wallet_list is None:
        wallet_list = wallet_info_from_excel()
    return wallet_list


# 根据浏览器序号从excel中读取数据
def find_wallet_by_index(index):
    list = load_wallet_list()

    key = AES_KEY
    if not key:
        logger.error("请在.env文件中配置密钥...")
        return None

    result = [x for x in list if x["index"] == index]
    if len(result) > 0:
        wallet = result[0]
        # # 解密数据
        # mnemo = aes_decrypt(wallet.get("w"), key)
        # wallet["w"] = mnemo

        # 解密数据
        pk = aes_decrypt(wallet.get("pk"), key)
        wallet["pk"] = pk

        return wallet

    return None


def find_ads_id_by_index(index):
    # 根据序号查找钱包信息
    wallet = find_wallet_by_index(index)
    if not wallet:
        logger.warning(f"index [{index}] 获取对应的钱包信息为空, 请检查配置项]")
        return None
    return wallet.get("ads_id")


# 根据ads指纹浏览器编号从excel中读取数据
def find_wallet_by_ads_id(ads_id):
    list = load_wallet_list()
    result = [x for x in list if x["ads_id"] == ads_id]
    if len(result) > 0:
        return result[0]

    return None
