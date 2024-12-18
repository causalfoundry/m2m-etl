from typing import Optional
import subprocess
import os
from ...util import util as u
from joblib import Parallel, delayed
from sqlalchemy import create_engine


def ingest_all_forms(
    since: str, until: str, format: str, destination: str
) -> Optional[Exception]:
    err = check_env_vars()
    if err is not None:
        return err
    all_det_files = os.listdir(get_det_folder())
    all_queries = sorted([os.path.splitext(f)[0] for f in all_det_files])
    results = Parallel(n_jobs=8, backend="loky")(
        delayed(ingest_form)(query_file, since, until, format, destination)
        for query_file in all_queries
    )
    errors = [err for err in results if err is not None]
    if errors:
        return Exception("\n".join([str(err) for err in errors]))
    return None


def ingest_form_for_month(
    query_file: str, year: int, month: int, format: str, destination: str
) -> Optional[Exception]:
    err = check_env_vars()
    if err is not None:
        return err
    since = u.get_first_date_of_month(year, month)
    until = u.get_first_date_of_next_month(year, month)
    target_file_name = get_target_filename_for_month(query_file, year, month, format)
    return ingest_form(query_file, since, until, format, destination, target_file_name)


def ingest_form(
    query_file: str,
    since: str,
    until: str,
    format: str,
    destination: str,
    target_file_name: str = None,
) -> Optional[Exception]:
    query_det_file = get_det_file(query_file)
    err = u.check_file_exists(query_det_file)
    if err is not None:
        return err

    if format not in ["xlsx", "parquet", "sql"]:
        return Exception("invalid format %s" % format)

    if format == "sql":
        return ingest_form_in_sql(query_file, since, until, destination)

    if destination is None:
        return Exception(
            "destination is required, it should be the folder from src if format is not sql"
        )

    if target_file_name is None:
        target_file_name = get_target_filename(query_file, since, until, format)

    destination_file = os.path.join(destination, target_file_name)

    if format == "xlsx":
        return ingest_form_in_xlsx(query_file, since, until, destination_file)
    else:
        return ingest_form_in_parquet(query_file, since, until, destination_file)


def ingest_form_in_xlsx(
    query_file: str, since: str, until: str, destination_file_from_src: str
) -> Optional[Exception]:
    u.makedirs(os.path.dirname(destination_file_from_src))

    run_commcare_export(
        query_det_file=get_det_file(query_file),
        since=since,
        until=until,
        output_destination=u.get_full_path(destination_file_from_src),
        output_format="xlsx",
    )
    return None


def ingest_form_in_parquet(
    query_file: str, since: str, until: str, destination_file_from_src: str
) -> Optional[Exception]:
    destination_xlsx = destination_file_from_src.replace(".parquet", ".xlsx")
    err = ingest_form_in_xlsx(
        query_file,
        since,
        until,
        destination_xlsx,
    )
    if err is not None:
        return err

    output_xlsx = u.get_full_path(destination_xlsx)
    output_parquet = output_xlsx.replace(".xlsx", ".parquet")
    err = u.xlsx_to_parquet(output_xlsx, output_parquet)
    if err is not None:
        return err
    os.remove(output_xlsx)
    return None


def ingest_form_in_sql(
    query_file: str, since: str, until: str, destination: str
) -> Optional[Exception]:
    try:
        _ = create_engine(destination)
    except Exception as e:
        return e
    run_commcare_export(
        query_det_file=get_det_file(query_file),
        since=since,
        until=until,
        output_destination=destination,
        output_format="sql",
    )
    return None


def run_commcare_export(
    query_det_file: str,
    since: str,
    until: str,
    output_destination: str,
    output_format: str,
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


def get_target_filename_for_month(
    query_file: str, year: int, month: int, format: str
) -> str:
    return "%s_%d_%d.%s" % (
        query_file,
        year,
        month,
        format,
    )


def get_target_filename(query_file: str, since: str, until: str, format: str) -> str:
    return "%s_%s_%s.%s" % (
        query_file,
        since.replace("-", "_"),
        until.replace("-", "_"),
        format,
    )


def get_det_folder() -> str:
    src_dir = u.find_src_dir()
    return os.path.join(src_dir, "streams", "stream1", "det_files")


def get_det_file(query_file: str) -> str:
    return os.path.join(get_det_folder(), "%s.xlsx" % query_file)


def check_env_vars() -> Optional[Exception]:
    err = u.check_env_var("COMMCARE_USERNAME")
    if err is not None:
        return err
    return u.check_env_var("COMMCARE_PASSWORD")
