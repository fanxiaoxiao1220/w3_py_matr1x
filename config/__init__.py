from os import environ
from dotenv import load_dotenv

load_dotenv()
AES_KEY = environ.get("AES_KEY")

# 日志存储目录
LOG_PATH = environ.get("LOG_PATH")

# 浏览器数据缓存配置
USER_DATA_PATH = environ.get("USER_DATA_PATH")


# 小狐狸钱包附件地址
METAMASK_PATH = environ.get("METAMASK_PATH")
# 小狐狸钱包访问地址
METAMASK_EXTENSION_PATH = environ.get("METAMASK_EXTENSION_PATH")
# bitget钱包地址
BITGET_EXTENSION_PATH = environ.get("BITGET_EXTENSION_PATH")
