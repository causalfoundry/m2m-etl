import os
import pandas as pd
from typing import Optional


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
