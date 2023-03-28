import base64
import json
import sys

PY_VERSION = sys.version_info.major


def b64encode(data):
    if PY_VERSION >= 3:
        return base64.b64encode(data.encode('utf-8'))
    return base64.b64encode(data)


def b64decode(data):
    if PY_VERSION >= 3:
        return base64.b64decode(data).decode('utf-8')
    return base64.b64decode(data)


def b64encode_json(data):
    if PY_VERSION >= 3:
        return base64.b64encode(json.dumps(data).encode('utf-8'))
    return base64.b64encode(json.dumps(data))


def b64decode_json(data):
    if PY_VERSION >= 3:
        return json.loads(base64.b64decode(data).decode('utf-8'))
    return json.loads(base64.b64decode(data))
