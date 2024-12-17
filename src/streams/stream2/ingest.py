from dhis2 import Api
from .util import Program, trackers_from_dicts
from typing import Optional, Tuple
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


def QueryProgramDetails(api: Api, program_id: str = None, start_date: str = None, end_date: str = None) -> Tuple[dict, Optional[Exception]]:
    """
    start/end_date accepts YYYY-MM-DD format.
    """
    if (start_date is None) ^ (end_date is None):
        return {}, ValueError(
            "start_date and end_date are mutually dependent. "
            "You must either specify both or neither.")
    if program_id is None:
        return {}, ValueError("tracker_id not specified!")

    # Logic intended to work out dataset Id list from trackerId
    dataset, err = GetProgramByID(api, program_id)
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
            'program': program_id,
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
        headers = [header["name"] for header in resp_data["headers"]]
        rows = resp_data["rows"]
        row_n = len(rows)
        for header in headers:
            ret[header] = []
        for row in rows:
            if len(row) != len(headers):
                return {}, Exception("Row length does not match column length")
            for header, col_value in zip(headers, row):
                ret[header].append(col_value)
            ret['Tracked entity name'] = list(
                metadata.values()) * row_n
            ret['Tracker id'] = [program_id] * row_n
            ret['Tracker display name'] = [tracker_name] * row_n

    return ret, None
