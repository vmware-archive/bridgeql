import base64
import importlib
import json
import socket
import sys

PY_VERSION = sys.version_info.major


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def local_ip_hostname():
    hostname = socket.getfqdn()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address, hostname


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


def load_function(function_str):
    mod_name, func_name = function_str.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)
