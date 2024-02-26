import pandas as pd
import json

import json
import numpy as np

from base.utils.aes import *
from config import AES_KEY


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class Excel:
    def __init__(self, excel_name):
        self.excel_name = excel_name

    # 全新写入数据
    def writeExcel(self, data):
        df = pd.DataFrame(data)

        # 将DataFrame对象写入Excel文件
        with pd.ExcelWriter(self.excel_name) as writer:
            df.to_excel(writer, index=False)

    # 追加数据
    def appendExcel(self, data):
        df = pd.read_excel(self.excel_name)
        new_data = pd.DataFrame(data)

        # 将新数据添加到原数据框中
        new_df = pd.concat([df, new_data], ignore_index=True)

        # 保存数据到 Excel 文件中
        new_df.to_excel(self.excel_name, index=False)

    def getItem(self, field_name, field_value):
        try:
            # 读取 Excel 文件
            df = pd.read_excel(self.excel_name)

            # 根据字段筛选行
            filtered_row = df.loc[df[field_name] == field_value]

            if len(filtered_row) == 0:
                raise Exception("No matching rows found.")

            # 获取第一行的标题
            titles = df.columns.tolist()
            # 获取第一行的值
            row_values = filtered_row.iloc[0].fillna("").tolist()

            # 创建 JSON 对象
            json_data = {}
            for title, value in zip(titles, row_values):
                json_data[title] = value

            # 转换为 JSON 格式
            return json_data
        except Exception as e:
            print("An error occurred while getItem rows from Excel:", str(e))
            return None

    # 根据字段删除行
    def deleteItem(self, field_name, field_value):
        # 读取 Excel 文件
        df = pd.read_excel(self.excel_name)

        # 根据字段筛选行
        filtered_rows = df.loc[df[field_name] == field_value]

        # 获取匹配行的索引
        row_indices = filtered_rows.index

        # 删除行
        df.drop(row_indices, inplace=True)

        # 保存数据到 Excel 文件中
        df.to_excel(self.excel_name, index=False)

    # 根据字段修改值
    def updateItem(self, field_name, field_value, updated_values):
        # 读取 Excel 文件
        df = pd.read_excel(self.excel_name)

        # 根据字段筛选行
        filtered_row = df.loc[df[field_name] == field_value]

        # 获取匹配行的索引
        row_index = filtered_row.index[0]

        # 修改值
        for column, updated_value in updated_values.items():
            df.at[row_index, column] = str(updated_value)

        # 保存数据到 Excel 文件中
        df.to_excel(self.excel_name, index=False)

    def readAllData(self):
        try:
            # 读取 Excel 文件
            df = pd.read_excel(self.excel_name)

            # 去除左右两边的空格
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

            # 转换为 JSON 格式
            # 转换为 JSON 格式
            json_data = df.to_json(orient="records")

            # 解析为 JSON 对象
            json_object = json.loads(json_data)

            # 返回 JSON 格式数据
            return json_object
        except Exception as e:
            print("获取所有数据并以 JSON 格式返回时出现错误:", str(e))
            return []

    # 加密方法
    def encryptPassword(self, password):
        if "=" in password:
            return password
        new_password = aes_encrypt(password, AES_KEY)
        return new_password

    # 解密方法
    def descryptPassword(self, password):
        new_password = aes_decrypt(password, AES_KEY)
        return new_password

    # 首次使用的时候工具方法，之后用不到
    # fileds 需要加密，或者解密的字段，以数组形式传入
    # is_encrypt 是否加密，是=加密 否=解密
    def encryptAndWritePassword(self, fileds=[], is_encrypt=True):
        try:
            # 读取 Excel 文件
            df = pd.read_excel(self.excel_name)

            for filed in fileds:
                # 将 NaN 值填充为空字符串
                df[filed].fillna("", inplace=True)

                # 将密码字段的浮点数转换为字符串类型
                df[filed] = df[filed].astype(str)

                # 加密非空密码字段
                if is_encrypt:
                    df.loc[df[filed] != "", filed] = df.loc[
                        df[filed] != "", filed
                    ].apply(self.encryptPassword)
                else:
                    df.loc[df[filed] != "", filed] = df.loc[
                        df[filed] != "", filed
                    ].apply(self.descryptPassword)

            # 将加密后的数据写入 Excel 文件
            df.to_excel(self.excel_name, index=False)

            print("密码字段已加密并成功写入 Excel 文件。")
        except Exception as e:
            print("加密并写入密码字段时出现错误:", str(e))
