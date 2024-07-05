from src.bizneo_requestor import get_absence_kinds, get_users, request_absence_for_user


class DataErrorException(Exception):
    pass


def create_absence_for_all_users(kind, start_at, end_at, comment=""):
    print(f"Creating absence of kind '{kind}' to all users [{start_at} - {end_at}] with comment '{comment}'")
    kind_id = get_kind_id_from_keyword(kind)
    for user in get_users():
        request_absence_for_user(kind_id, start_at, end_at, comment, user.user_id)


def get_kind_id_from_keyword(keyword):
    absence_kinds = get_absence_kinds()
    for absence_kind in absence_kinds:
        if absence_kind.has_keyword(keyword):
            return absence_kind.kind_id
    raise DataErrorException(
        f"We haven't found the keyword {keyword} among our abscense kinds:\n{absence_kinds}"
    )
