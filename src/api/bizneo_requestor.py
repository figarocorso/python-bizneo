import requests

from src.api.absence_kind import AbsenceKind
from src.api.user import User
from src.api.schedule import Schedule


URL = "https://sysdig.bizneohr.com"
TOKEN = ""
TOKEN_PARAMETER = f"?token={TOKEN}"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class RequestFailedException(Exception):
    pass


def get_absence_kinds():
    response = _get_request_json(f"{URL}/api/v1/absence-kinds/{TOKEN_PARAMETER}")
    absence_kinds = []
    for kind in response.get("kinds", []):
        absence_kinds.append(AbsenceKind.from_dict(kind))
    return absence_kinds


def get_user(user_id):
    get_user_url = f"{URL}/api/v1/users/{user_id}/{TOKEN_PARAMETER}"
    response = _get_request_json(get_user_url)
    return User.from_dict(response.get("user", {}))


def get_users():
    page_number = 1
    total_pages = 2
    get_users_url = f"{URL}/api/v1/users/{TOKEN_PARAMETER}&page={{page_number}}"
    users = []
    while page_number <= total_pages:
        response = _get_request_json(get_users_url.format(page_number=page_number))
        page_number += 1
        total_pages = response.get("pagination", []).get("total_pages", 0)
        for user in response.get("users", []):
            users.append(User.from_dict(user))

    return users


def get_user_schedules(user_id, start_at, end_at):
    get_user_url = (
        f"{URL}/api/v1/users/{user_id}/schedules/{TOKEN_PARAMETER}&start_at={start_at}&end_at={end_at}"
    )
    return _get_instance_list_from_paginated_get_request(get_user_url, "day_details", Schedule)


def request_absence_for_user(kind_id, start_at, end_at, comment, user_id):
    print(f"adding absence for user {user_id}")
    absence_data = {
        "absence": {
            "kind_id": kind_id,
            "start_at": start_at,
            "end_at": end_at,
            "comment": comment,
        }
    }
    _post_request_json(f"{URL}/api/v1/users/{user_id}/absences{TOKEN_PARAMETER}", absence_data)


def _get_instance_list_from_paginated_get_request(url, data_dict_key, data_class):
    page_number = 1
    total_pages = 2
    data_url = f"{url}&page={{page_number}}"
    data_list = []
    while page_number <= total_pages:
        response = _get_request_json(data_url.format(page_number=page_number))
        page_number += 1
        total_pages = response.get("pagination", []).get("total_pages", 0)
        for data_item in response.get(data_dict_key, []):
            data_list.append(data_class.from_dict(data_item))

    return data_list


def _get_request_json(url):
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        raise RequestFailedException(f"Request {url} failed with status code {response.status_code}")
    return response.json()


def _post_request_json(url, data):
    response = requests.post(url, headers=HEADERS, json=data)
    if not response.ok:
        if response.status_code == 409:
            print(f"Conflict for {data}")
            return {}
        raise RequestFailedException(f"Request {url} failed with status code {response.status_code}")

    return response.json()
