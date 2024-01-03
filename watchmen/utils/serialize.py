import json
from common.handle import Request


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Request):
            return obj.into_dict()
        else:
            return json.JSONEncoder.default(obj)
