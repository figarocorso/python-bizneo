import requests

from src.api.absence_kind import AbsenceKind
from src.api.user import User


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
