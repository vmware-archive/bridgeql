import base64
import json


def b64encode_json(data):
    return base64.b64encode(json.dumps(data).encode('utf-8'))


def b64decode_json(data):
    return json.loads(base64.b64decode(data).decode('utf-8'))
