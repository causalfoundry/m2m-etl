from .ingest import GetAllPrograms, GetProgramByID, GetTrackerRawDataWithinDateRange
from dhis2 import Api
import json
import os


def test_tracker():
    url = os.environ.get("url")
    username = os.environ.get("username")
    password = os.environ.get("password")
    api = Api(url, username, password)

    (ret, err) = GetAllPrograms(api, None)
    assert err is None

    for tracker in ret:
        print('-----------')
        print(tracker.id, tracker.display_name)
        tr, err = GetProgramByID(api, tracker.id)
        assert err is None
        print('-----------')
        print(tr.keys(), len(tr.keys()))
        tr, err = GetTrackerRawDataWithinDateRange(api, tracker.id, None, None)
        break
        # print('-----------')
        # print(tr)
