class Program:
    def __init__(self, id: str, display_name: str):
        self.id = id
        self.display_name = display_name

    def __repr__(self):
        return f"Tracker(id='{self.id}', display_name='{self.display_name}')"

    def to_dict(self):
        return {
            "id": self.id,
            "display_name": self.display_name
        }


def tracker_from_dict(d: dict) -> Program:
    return Program(id=d["id"], display_name=d["displayName"])


def trackers_from_dicts(dict_list: list[dict]) -> list[Program]:
    return [tracker_from_dict(d) for d in dict_list]
