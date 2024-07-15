from src.api.bizneo_requestor import (
    get_absence_kinds,
    get_user,
    get_users,
    request_absence_for_user,
    get_user_schedules,
    get_user_logged_times,
)


class DataErrorException(Exception):
    pass


def create_absence_for_user(user_id, kind, start_at, end_at, comment=""):
    print(
        f"Creating absence to user {user_id} of kind '{kind}' "
        f"[{start_at} - {end_at}] with comment '{comment}'"
    )
    kind_id = get_kind_id_from_keyword(kind)
    user = get_user(user_id)
    request_absence_for_user(kind_id, start_at, end_at, comment, user.user_id)


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


def get_time_report_for_taxon(taxon, start_at, end_at):
    users_in_taxon = [user for user in get_users() if taxon.lower() in user.main_taxons.lower()]
    users_report = []
    for user in users_in_taxon:
        schedules = get_user_schedules(user.user_id, start_at, end_at)
        logged_times = get_user_logged_times(user.user_id, start_at, end_at)
        users_report.append({"user": user, "schedules": schedules, "logged_times": logged_times})
