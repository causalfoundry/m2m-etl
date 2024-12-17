from dhis2 import Api
from .util import Program, trackers_from_dicts
from typing import Optional, Tuple
import pandas as pd
import json


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
    if id is None:
        return None, ValueError("tracker_id not specified!")

    # for raw tracker data by Id
    query = f'/programs/{id}'
    response = api.get(query, params={'fields': '*'})
    return response.json(), None


def GetTrackerRawDataWithinDateRange(api: Api, tracker_id: str = None, start_date: str = None, end_date: str = None) -> Tuple[dict, Optional[Exception]]:
    """
    possibly to implement a date format checker as well for
    start_date and end_date using datetime
    start/end_date accepts YYYY-MM-DD format for now.
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
        ret = {}
        headers = resp_data["headers"]
        row_n = len(resp_data["rows"])
        for (i, column) in enumerate(headers):
            col = column['name']
            for row in resp_data["rows"]:
                if col not in ret:
                    ret[col] = []
                ret[col].append(row[i])
            if len(ret) > 0:
                ret['Tracked entity name'] = list(
                    metadata.values()) * row_n
                ret['Tracker id'] = [tracker_id] * row_n
                ret['Tracker display name'] = [tracker_name] * row_n
    return ret, None
