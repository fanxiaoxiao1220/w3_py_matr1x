import os
import datetime
import shutil


def get_project_root_path():
    # 获取当前脚本的目录（包括文件名）
    current_script_path = os.path.abspath(__file__)
    # 获取项目根节点的路径
    project_root = os.path.dirname(os.path.dirname(current_script_path))

    return project_root


def get_current_datetime(format="%Y-%m-%d %H:%M:%S"):
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()
    # 格式化日期时间为字符串
    formatted_date = current_datetime.strftime(format)
    return formatted_date


def clear_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"The folder {folder_path} has been cleared.")
    except FileNotFoundError:
        print(f"The folder {folder_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
