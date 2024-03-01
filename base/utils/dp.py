import os
from DrissionPage import ChromiumPage, ChromiumOptions
from fake_useragent import UserAgent
from loguru import logger


from base.utils.adspower import *
from base.utils.bit import get_debug_address_with_bite
from config import USER_DATA_PATH, METAMASK_PATH


# adspower指纹浏览器
def get_page_by_adspwer_id(id):
    debugger_address = get_address_with_adspower(id)
    return ChromiumPage(addr_driver_opts=debugger_address)


# 比特指纹浏览器
def get_page_by_bit_id(id):
    debugger_address = get_debug_address_with_bite(id)
    return ChromiumPage(addr_driver_opts=debugger_address)


# 自动获取系统浏览器
def get_page_auto():
    co = ChromiumOptions().auto_port()
    return ChromiumPage(co)


# 已有的浏览器用户
def get_page_by_browser_user():
    co = ChromiumOptions()
    # 从已有的浏览器用户进行调试
    co.use_system_user_path(on_off=True)
    return ChromiumPage(addr_or_opts=co)


# # 目前仅支持 adspower 指纹浏览器
# # name adspower为账号ID 示例：j5s7k80
# def get_page_by_name(name=""):
#     if len(name) == ZERO:
#         co = ChromiumOptions().auto_port()
#         return WebPage(co)
#     elif len(name) == ADS_ID:
#         debugger_address = get_address_with_adspower(id)
#         return WebPage(addr_driver_opts=debugger_address)
#     else:
#         return get_page_with_browser_name(name)


def get_page_with_browser_name(name, data):
    co = _get_system_browser_options(name, data)
    return ChromiumPage(co)


# 获取options
def _get_system_browser_options(name, data):

    co = ChromiumOptions().auto_port(True)
    if not data:
        raise Exception(f"输入的 {name} 不存在, 请检查")

    # 设置UA、代理IP、用户缓存
    ua = data.get("ua")
    proxy = data.get("proxy")
    if bool(ua):
        co.set_user_agent(ua)
    if bool(proxy):
        logger.info(f"{name} ip: {proxy}")
        parts = proxy.split(":")
        # 无用户名密码直接用浏览器接口
        if len(parts) == 2:
            co.set_proxy(f"http://{proxy}")
        if len(parts) == 3:
            co.set_proxy(proxy)

    user_data_path = rf"{USER_DATA_PATH}/{name}"
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)

    co.set_paths(user_data_path=user_data_path)
    if METAMASK_PATH:
        _path = rf"{METAMASK_PATH}"
        co.add_extension(_path)

    return co
