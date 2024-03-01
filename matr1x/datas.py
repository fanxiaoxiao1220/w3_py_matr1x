import os
from loguru import logger
from base.utils.excel import Excel
from base.utils.aes import aes_decrypt, aes_encrypt
from config import AES_KEY
from utils.hhtime import get_current_date

data_list = None


def file_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "datas.xlsx")


def get_infos_from_excel():
    return Excel(file_path()).readAllData()


def load_data_list():
    data_list = get_infos_from_excel()
    for data in data_list:
        pk = data.get("pk")
        w = data.get("w")
        if pk:
            _pk = aes_decrypt(pk, AES_KEY)
            data["pk"] = _pk

        if w:
            _w = aes_decrypt(w, AES_KEY)
            data["w"] = _w
    return data_list
    # return [data_list[41]]


# 根据浏览器序号从excel中读取数据
def find_data_by_index(index):
    list = load_data_list()

    key = AES_KEY
    if not key:
        logger.error("请在.env文件中配置密钥...")
        return None

    result = [x for x in list if x["index"] == index]
    if len(result) > 0:
        wallet = result[0]
        return wallet

    return None


def update_key(index, key_count=0):
    excel = Excel(file_path())
    timestamp = get_current_date()
    excel.updateItem(
        "index",
        index,
        {
            "key": key_count,
        },
    )


def update_imported(index):
    excel = Excel(file_path())
    timestamp = get_current_date()
    excel.updateItem(
        "index",
        index,
        {
            "imported": 1,
        },
    )


def update_point(index, point):
    excel = Excel(file_path())
    logger.info(f"{point}积分写入 {index} ")
    excel.updateItem(
        "index",
        index,
        {
            "point": str(point),
        },
    )


def update_last_point(index, last_point):
    excel = Excel(file_path())
    excel.updateItem(
        "index",
        index,
        {
            "last_point": str(last_point),
        },
    )


def update_registed(index):
    excel = Excel(file_path())
    excel.updateItem(
        "index",
        index,
        {"invite_code": None, "registed": "1"},
    )


def update_claimed_date(index):
    excel = Excel(file_path())
    timestamp = get_current_date()
    excel.updateItem(
        "index",
        index,
        {"claimed_date": timestamp},
    )


def insert_data(eth_address, w, pk, pwd, ua):
    w = aes_encrypt(w, AES_KEY)
    pk = aes_encrypt(pk, AES_KEY)
    pwd = aes_encrypt(pwd, AES_KEY)

    excel = Excel(file_path())
    index = excel.get_row_count() + 1

    data = {
        "index": index,
        "address": eth_address,
        "pk": pk,
        "w": w,
        "pwd": pwd,
        "ua": ua,
    }

    excel.appendExcel(data)
