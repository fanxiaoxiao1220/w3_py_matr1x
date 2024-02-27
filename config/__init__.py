from os import environ
from dotenv import load_dotenv

load_dotenv()
AES_KEY = environ.get("AES_KEY")

# 日志存储目录
LOG_PATH = environ.get("LOG_PATH")

# 浏览器数据缓存配置
USER_DATA_PATH = environ.get("USER_DATA_PATH")

# polygon api key
POLYGON_API_KEY = environ.get("POLYGON_API_KEY")

# 小狐狸钱包附件地址
METAMASK_PATH = environ.get("METAMASK_PATH")
# 小狐狸钱包访问地址
METAMASK_EXTENSION_PATH = environ.get("METAMASK_EXTENSION_PATH")
