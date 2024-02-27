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


def get_page_with_browser_name(name):

    # co = _get_system_browser_options(name)
    co = ChromiumOptions().auto_port()
    return ChromiumPage(co)


# 获取options
def _get_system_browser_options(name):

    co = ChromiumOptions().auto_port(True)

    # # 设置UA、代理IP、用户缓存
    # if bool(browser.user_agent):
    #     co.set_user_agent(browser.user_agent)
    # if bool(browser.ip_address):
    #     logger.info(f"{name} ip: {browser.ip_address}")
    #     parts = browser.ip_address.split(":")
    #     # 无用户名密码直接用浏览器接口
    #     if len(parts) == 2:
    #         co.set_proxy(f"http://{browser.ip_address}")
    #     if len(parts) == 3:
    #         co.set_proxy(browser.ip_address)
    #     # 需要授权的，调用浏览器插件
    #     elif len(parts) == 4:
    #         host = parts[0]
    #         port = parts[1]
    #         username = parts[2]
    #         pwd = parts[3]
    #         extension_path = _get_auth_proxy_extention(host, port, username, pwd)
    #         logger.debug(f"extension_path {extension_path}")
    #         co.add_extension(extension_path)

    # user_data_path = rf"{USER_DATA_PATH}/{name}"
    # co.set_paths(user_data_path=user_data_path)
    # if METAMASK_PATH:
    #     co.add_extension(rf"{METAMASK_PATH}")

    # return co
