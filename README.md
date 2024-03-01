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

  `POLYGON_RPC` polygon rpc , https://infura.io 注册申请

- matr1x 文件夹下 `datas.xlsx1` 改为 `datas.xlsx`
  更改后需初始化数据 `index`,`ads_id`,`address`,`pk`, `pwd` 这几个字段
  `ads_id` adspower 指纹浏览器的编号
  `address` eth 钱包地址
  `pk` 钱包私钥，需要通过 aes 加密存储
  `pwd` 小狐狸钱包密码

### 2. 数据生成+配置

批量生成 10 条数据

`python3 helper.py gd -c 10`

还需手工配置字段：
`invite_code`： 邀请码， 首次需向其他人获取，激活第二天后，可以执行 `python index.py rc` 后在 `codes.txt` 获取
`tw_token`： twitter 登录 token 可在 https://hstock.org/ru/category/twitter 购买
`proxy`：代理， 可选，配置了会更安全，目前只支持不带授权的代理

字段配置完成后，就可以下一步了。

### 3. 执行- 单个执行

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

- 获取所有浏览器中的邀请码
  `python index.py rc`
  获取后写入`codes.txt`文件中

- 获取某个浏览器的邀请码
  `python index.py codes -i 1`
