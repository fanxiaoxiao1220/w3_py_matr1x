# w3_py_matr1x

matr1x 自动化任务系统, 目前只支持基于 adspower 指纹浏览器进行批量操作

前提：

1. 需要导入小狐狸钱包私钥
2. 导入 twitter 账号

## 前置

### 0. 安装

`pip3 install -r requirements.txt`

### 1. 配置

- `.env_example` 改为 `.env`

  `AES_KEY` 是 aes 密钥，长度需要固定 16 位

  `POLYGON_API_KEY` polygon api key, https://polygonscan.com/login 注册申请`api_key`

- config 文件夹下 `/eth_wallet.xlsx1` 改为 `eth_wallet.xlsx`
  更改后初始化数据

- matr1x 文件夹下 `datas.xlsx1` 改为 `datas.xlsx`
  更改后需初始化数据 `index`,`ads_id`,`address`,`pk` 这几个字段

### 2. 执行

- 单个执行
  `python index.py ri -i index`
  这里的`index`就是 `matr1x/data.xlsx`表格中`index`

- 随机批量执行
  `python index.py r`
  批量执行默认 4 个进程同时进行，也可以自定义添加，添加命令如下：
  `python index.py r -c 5`

      * 通过合约领取钥匙
      `python index.py claim -i 2 -c 3`

      * 批量查询余额，低于0.5马蹄会告警
      `python index.py b`
