from .ingest import GetAllPrograms, GetProgramByID, QueryProgramDetails
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

    for id in ret:
        print(id.id, id.display_name)
        tr, err = GetProgramByID(api, id.id)
        print(json.dumps(tr, indent=4))
        assert err is None
        tr, err = QueryProgramDetails(api, id.id, None, None)
        print(json.dumps(tr, indent=4))
