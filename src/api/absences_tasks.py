from src.api.bizneo_requestor import (
    delete_absence,
    get_absence_kinds,
    get_user,
    get_user_absences,
    get_users,
    request_absence_for_user,
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


def delete_absence_for_user(user_id, start_at, end_at, dry_run=False):
    print(f"{'[DRY-RUN] ' if dry_run else ''}Searching absences for user {user_id} [{start_at} - {end_at}]")
    user = get_user(user_id)
    absences = get_user_absences(user.user_id, start_at, end_at)

    # Filter absences by user_id and date range
    matching_absences = [
        a for a in absences if a.matches_user(user.user_id) and a.matches_dates(start_at, end_at)
    ]

    if not matching_absences:
        print(f"  No absences found for user {user.first_name} {user.last_name} in date range")
        return 0

    deleted_count = 0
    for absence in matching_absences:
        if dry_run:
            print(
                f"  [DRY-RUN] Would delete absence {absence.absence_id} "
                f"for {user.first_name} {user.last_name}"
            )
        else:
            success = delete_absence(absence.absence_id)
            if success:
                print(f"  Deleted absence {absence.absence_id} for {user.first_name} {user.last_name}")
                deleted_count += 1

    return deleted_count if not dry_run else len(matching_absences)


def delete_absence_for_all_users(start_at, end_at, dry_run=False):
    print(f"{'[DRY-RUN] ' if dry_run else ''}Deleting absences for all users [{start_at} - {end_at}]")
    total_deleted = 0
    for user in get_users():
        deleted = delete_absence_for_user(user.user_id, start_at, end_at, dry_run)
        total_deleted += deleted

    print(f"\n{'[DRY-RUN] Would delete' if dry_run else 'Deleted'} {total_deleted} absence(s) in total")
    return total_deleted


def get_kind_id_from_keyword(keyword):
    absence_kinds = get_absence_kinds()
    for absence_kind in absence_kinds:
        if absence_kind.has_keyword(keyword):
            return absence_kind.kind_id
    raise DataErrorException(
        f"We haven't found the keyword {keyword} among our abscense kinds:\n{absence_kinds}"
    )
