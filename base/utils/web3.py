from web3 import Web3
from eth_account import Account
from web3.middleware import geth_poa_middleware


def get_pk_4_phrase(mnemonic_phrase, node_url=None):
    # 创建一个带有指定提供者的 Web3 实例（或者使用默认的本地节点）
    web3 = Web3(Web3.HTTPProvider(node_url)) if node_url else Web3()

    # 注入 PoA 兼容性中间件（如果使用 PoA 网络）
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # 启用助记词功能
    Account.enable_unaudited_hdwallet_features()

    try:
        # 从助记词中推导出私钥
        private_key_hex = Account.from_mnemonic(mnemonic_phrase)._private_key.hex()
        private_key_str = str(private_key_hex)
        # print("以太坊私钥:", private_key_str)

        return private_key_str
    except ValueError as e:
        print(f"错误: {e}")
        return None
