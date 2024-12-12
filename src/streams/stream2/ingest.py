from dhis2 import Api
from typing import Optional, Tuple


class Tracker:
    def __init__(self, id: str, display_name: str):
        self.id = id
        self.display_name = display_name

    def __repr__(self):
        return f"Tracker(id='{self.id}', display_name='{self.display_name}')"


def create_trackers_from_dicts(dict_list: list[dict]) -> list[Tracker]:
    return [Tracker(id=d["id"], display_name=d["displayName"]) for d in dict_list]


def GetAllTrackers(api: Api) -> Tuple[list[Tracker], Optional[Exception]]:
    temp = api.get_paged("programs", merge=True)
    if not isinstance(temp, dict):
        return [], Exception("response is not a dictionary")
    if "programs" not in temp:
        return [], Exception("programs key not found in response")
    all_data = temp["programs"]
    return create_trackers_from_dicts(all_data), None
