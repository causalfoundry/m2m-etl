from .dhis2 import GetAllPrograms
from dhis2 import Api
import json
import os


def test_read_program():
    url = os.environ.get("url")
    username = os.environ.get("username")
    password = os.environ.get("password")
    api = Api(url, username, password)

    (programs, err) = GetAllPrograms(api, None)
    assert err is None

    for program in programs:
        program.populate(api)
        assert program.detailed_program is not None
        print(json.dumps(program.detailed_program, indent=4))
        ret, err = program.query_program(api, None, None)
        assert err is None
        print(json.dumps(ret, indent=4))
        break
