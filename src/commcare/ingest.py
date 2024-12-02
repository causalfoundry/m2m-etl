from typing import Optional
import subprocess
import os
import util as u
from joblib import Parallel, delayed


def ingest_all(date: str) -> Optional[Exception]:
    err = check_env_vars()
    if err is not None:
        return err
    all_files = os.listdir("./det_files")
    all_files_without_ext = sorted([os.path.splitext(f)[0] for f in all_files])
    results = Parallel(n_jobs=8, backend="loky")(
        delayed(ingest_file)(file, date) for file in all_files_without_ext
    )
    errors = [err for err in results if err is not None]
    if errors:
        return Exception("\n".join([str(err) for err in errors]))
    return None


def ingest_file(query_file: str, date: str) -> Optional[Exception]:
    query_det_file = "./det_files/%s.xlsx" % query_file
    if not os.path.exists(query_det_file):
        return Exception("error file %s does not exist" % query_det_file)
    date_folder = date.replace("-", "_")
    parquet_folder = "./parquet_files/%s" % date_folder
    os.makedirs(parquet_folder, exist_ok=True)
    output_xlsx = "%s/%s.xlsx" % (parquet_folder, query_file)
    run_commcare_export(
        query_det_file=query_det_file,
        since=date,
        until=u.add_days_to_date(date, 1),
        output_destination=output_xlsx,
    )
    output_parquet = output_xlsx.replace(".xlsx", ".parquet")
    err = u.xlsx_to_parquet(output_xlsx, output_parquet)
    if err is not None:
        return err
    os.remove(output_xlsx)
    return None


def run_commcare_export(
    query_det_file: str,
    since: str,
    until: str,
    output_destination: str,
    *,
    output_format: str = "xlsx",
):
    command = "commcare-export"
    args = {
        "--output-format": output_format,
        "--project": "m2m",
        "--username": os.getenv("COMMCARE_USERNAME"),
        "--password": os.getenv("COMMCARE_PASSWORD"),
        "--query": query_det_file,
        "--since": since,
        "--until": until,
        "--output": output_destination,
    }
    cmd = [command] + [str(item) for pair in args.items() for item in pair]
    with open(os.devnull, "wb") as devnull:
        subprocess.run(
            cmd,
            text=True,
            stdin=devnull,
            stdout=devnull,
            stderr=devnull,
        )


def check_env_vars() -> Optional[Exception]:
    err = u.check_env_var("COMMCARE_USERNAME")
    if err is not None:
        return err
    return u.check_env_var("COMMCARE_PASSWORD")
