import os
import pandas as pd
from typing import Optional


def get_full_path(path: str) -> str:
    src_dir = find_src_dir()
    return os.path.join(src_dir, path)


def makedirs(folder_from_src: str):
    src_dir = find_src_dir()
    return os.makedirs(os.path.join(src_dir, folder_from_src), exist_ok=True)


def find_src_dir():
    path_split = os.path.abspath(__file__).split("/")
    src_index = last_index(path_split, "src")
    return "/".join(path_split[: src_index + 1])


def xlsx_to_parquet(input_xlsx: str, output_parquet: str) -> Optional[Exception]:
    try:
        df = pd.read_excel(input_xlsx, engine="openpyxl")
        df.to_parquet(output_parquet, engine="pyarrow", index=False)
    except Exception as e:
        return e


def add_days_to_date(date_str: str, days: int) -> str:
    return (pd.to_datetime(date_str) + pd.Timedelta(days=days)).strftime("%Y-%m-%d")


def check_env_var(var_name: str) -> Optional[Exception]:
    if os.getenv(var_name) is None:
        return Exception("error the env variable %s is not set" % var_name)
    return None


def check_file_exists(file_path: str) -> Optional[Exception]:
    if not os.path.exists(file_path):
        return Exception("error file %s does not exist" % file_path)
    return None


def last_index(lst: list, item: str) -> int:
    rev_lst = lst[::-1]
    first_occ = rev_lst.index(item)
    return len(lst) - first_occ - 1
