from .gcp_blob import upload_json_to_blob, read_json_from_blob


def test_upload_blob():
    upload_json_to_blob("m2m-warehouse", {"hello": "world"}, "demo.json")
    ret = read_json_from_blob("m2m-warehouse", "demo.json")
    print(ret)
