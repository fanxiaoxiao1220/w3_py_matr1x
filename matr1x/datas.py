import os
from loguru import logger
from base.utils.excel import Excel
from base.utils.aes import aes_decrypt
from config import AES_KEY
from utils.hhtime import get_current_date

data_list = None


def file_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "datas.xlsx")


def get_infos_from_excel():
    return Excel(file_path()).readAllData()


def load_data_list():
    global data_list
    if data_list is None:
        data_list = get_infos_from_excel()
        for data in data_list:
            pk = data.get("pk")
            if pk:
                newpk = aes_decrypt(pk, AES_KEY)
                data["pk"] = newpk
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


def update_point(index, point, last_point, key_count=0):
    excel = Excel(file_path())
    logger.info(f"{point}积分写入 {index} ")
    timestamp = get_current_date()
    excel.updateItem(
        "index",
        index,
        {
            "point": point,
            "last_point": last_point,
            "key": key_count,
            "claimed_date": timestamp,
        },
    )


def update_registed(address):
    excel = Excel(file_path())
    excel.updateItem(
        "address",
        address,
        {"url": None, "registed": "1"},
    )
