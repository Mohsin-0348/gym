import random
import re
import string
import uuid

from django.conf import settings


def generate_auth_key():
    key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
    key = 'w3AC' + key
    return key


def create_token():
    return uuid.uuid4()


def build_absolute_uri(path) -> str:
    return f"http://{settings.SITE_URL}/{path}"


def get_json_data(request) -> object:
    data = {i[0]: i[1] for i in request.META.items() if i[0].startswith('HTTP_')}
    return data


def email_checker(email):
    regex = r"^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    if (re.search(regex, email)):
        return True
    return False


def username_validator(name):
    regex = r'^[\w][\w\d_]+$'
    if (re.search(regex, name)):
        return True
    return False


def divide_chunks(list_d, n):
    for i in range(0, len(list_d), n):
        yield list_d[i: i + n]


def get_tenant():
    domain = None
    return domain
