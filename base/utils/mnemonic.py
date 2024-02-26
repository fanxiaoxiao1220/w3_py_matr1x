# 生成24个英语单词
def generate_mnemo_24():
    from mnemonic import Mnemonic

    mnemo = Mnemonic("english")
    return mnemo.generate(256)


# 生成12个英语单词
def generate_mnemo_12():
    from mnemonic import Mnemonic

    mnemo = Mnemonic("english")
    return mnemo.generate(128)
