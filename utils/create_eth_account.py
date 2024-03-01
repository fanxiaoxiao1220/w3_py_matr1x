from eth_account import Account
from mnemonic import Mnemonic
import os
import time

# 启用未经审核的HD钱包功能
Account.enable_unaudited_hdwallet_features()


def get_pk_from_mnemo(mnemo):
    wallet = Account.from_mnemonic(mnemo)
    print(wallet.address)
    print(wallet.key.hex())
    return wallet.key.hex()


def generate_accounts(_num_accounts):
    _accounts = []
    mnemo = Mnemonic("english")

    for i in range(_num_accounts):
        mnemonic = mnemo.generate(strength=128)
        wallet = Account.from_mnemonic(mnemonic)
        _accounts.append(
            (
                wallet.key.hex(),
                mnemonic,
                wallet.address,
            )
        )

    return _accounts


def main_generate_accounts(_num_accounts):
    accounts = generate_accounts(_num_accounts)
    output = "\n".join([",".join(account) for account in accounts])
    os.makedirs("config", exist_ok=True)
    time_stamp = int(time.time())
    filename = f"config/accounts_{time_stamp}.csv"
    with open(filename, "w") as f:
        f.write(output)


if __name__ == "__main__":
    _num_accounts = 100
    main_generate_accounts(_num_accounts)
