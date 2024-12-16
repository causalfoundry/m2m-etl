from dhis2 import Api
from .util import Program, trackers_from_dicts
from typing import Optional, Tuple
import pandas as pd


def GetAllPrograms(api: Api, page_size=None) -> Tuple[list[Program], Optional[Exception]]:
    if page_size is not None:
        temp = api.get_paged("programs", page_size=page_size)
    else:
        temp = api.get_paged("programs", merge=True)
    if not isinstance(temp, dict):
        return [], Exception("response is not a dictionary")
    if "programs" not in temp:
        return [], Exception("programs key not found in response")
    all_data = temp["programs"]
    return trackers_from_dicts(all_data), None


def GetProgramByID(api: Api, id=None) -> Tuple[dict, Optional[Exception]]:
    if id:
        # for raw tracker data by Id
        query = f'/programs/{id}'
        response = api.get(query, params={'fields': '*'})
        return response.json(), None
    return None, ValueError("tracker_id not specified!")


def GetTrackerRawDataWithinDateRange(api: Api, tracker_id: str = None, start_date=None, end_date=None) -> Tuple[dict, Optional[Exception]]:
    """
            possibly to implement a date format checker as well for 
            start_date and end_date using datetime

            Accepts YYYY-MM-DD format for now.

            args:
                    how you structure the params field determines the URL that will be constructed by
                    the dhis2 api
    """
    if (start_date is None) ^ (end_date is None):
        return {}, ValueError(
            "start_date and end_date are mutually dependent. "
            "You must either specify both or neither.")
    if tracker_id is None:
        return {}, ValueError("tracker_id not specified!")

    # Logic intended to work out dataset Id list from trackerId
    dataset, err = GetProgramByID(api, tracker_id)
    if err is not None:
        return None, err
    # Display name of the tracker:
    tracker_name = dataset['name']
    # logging.info(tracker_name)
    response_per_id = []
    for org_id in dataset['organisationUnits']:
        response = api.get('trackedEntityInstances/query', params={
            'ou': org_id["id"],
            'startDate': start_date,
            'endDate':  end_date,
            'program': tracker_id,
            'ouMode': 'SELECTED',
        }
        )
        resp_data = response.json()
        # response format
        """
        "headers": [
                {
                    "name": "instance",
                    "column": "Instance",
                    "type": "java.lang.String",
                    "hidden": false,
                    "meta": false
                },
            ],
        "metaData": {
            "names": {},
            "pager": {
                "page": 1,
                "total": 0,
                "pageSize": 50,
                "pageCount": 1
            }
        },
        "rows": [],
        "headerWidth": 13,
        "width": 0,
        "height": 0
        """
        metadata = resp_data['metaData']['names']
        tmp_dict = {}
        headers = resp_data["headers"]
        return None, None
        for col, (_, rows) in zip(headers, enumerate(resp_data["rows"])):
            tmp_dict[col["column"]] = []
        for col, (i, rows) in zip(tmp_dict.keys(), enumerate(resp_data["rows"])):
            if len(rows) > 1:
                tmp_dict[col].append(f"{rows[i]}")
            elif len(rows) == 0:
                tmp_dict[col].append([])
        if len(tmp_dict) > 1:
            dfs = pd.DataFrame.from_dict(tmp_dict)
            dfs["Tracked entity name"] = list(metadata.values())[0]
            dfs["Tracker id"] = tracker_id
            dfs["Tracker displayName"] = tracker_name
            if "Telephone number" in dfs.columns:
                # if the numbers are nine put zero in the first position of phone number
                dfs["Telephone number"] = dfs["Telephone number"].astype(
                    str).str.zfill(10).fillna('0')
            # logging.info(dfs)
            response_per_id.append(dfs)

    return [pd.DataFrame(resp) for resp in response_per_id], None
