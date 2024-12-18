from dhis2 import Api
from typing import Optional, Tuple


class Program:
    def __init__(self, id: str, display_name: str):
        self.id = id
        self.display_name = display_name
        self.name = None
        self.organization_units = None
        self.detailed_program = None

    def __repr__(self):
        return f"Program(id='{self.id}', display_name='{self.display_name}')"

    def to_dict(self):
        return {
            "id": self.id,
            "display_name": self.display_name
        }

    def populate(self, api: Api) -> Optional[Exception]:
        self.detailed_program, err = _get_program_by_id(api, self.id)
        if err is not None:
            return err
        self.name = self.detailed_program['name']
        self.organization_units = self.detailed_program['organisationUnits']
        return

    def query_program(self, api: Api, start_date: str = None, end_date: str = None) -> Tuple[dict, Optional[Exception]]:
        """
        start/end_date accepts YYYY-MM-DD format.
        """
        if (start_date is None) ^ (end_date is None):
            return {}, ValueError(
                "start_date and end_date are mutually dependent. "
                "You must either specify both or neither.")
        if self.id is None:
            return {}, ValueError("tracker_id not specified!")

        if self.detailed_program is None:
            self.populate(api)

        # Logic intended to work out dataset Id list from trackerId
        # Display name of the program:
        for org_id in self.organization_units:
            response = api.get('trackedEntityInstances/query', params={
                'ou': org_id["id"],
                'startDate': start_date,
                'endDate':  end_date,
                'program': self.id,
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
                ret['Program entity name'] = list(
                    metadata.values()) * row_n
                ret['Program id'] = [self.id] * row_n
                ret['Program display name'] = [self.name] * row_n

        return ret, None


def program_from_dict(d: dict) -> Program:
    return Program(id=d["id"], display_name=d["displayName"])


def programs_from_dicts(dict_list: list[dict]) -> list[Program]:
    return [program_from_dict(d) for d in dict_list]


def _get_program_by_id(api: Api, id: str) -> Tuple[dict, Optional[Exception]]:
    if id is None:
        return None, ValueError("tracker_id not specified!")

    # for raw tracker data by Id
    query = f'/programs/{id}'
    response = api.get(query, params={'fields': '*'})
    return response.json(), None


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
    return programs_from_dicts(all_data), None
