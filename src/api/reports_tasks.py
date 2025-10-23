from src.api.bizneo_requestor import get_user_logged_times, get_user_schedules, get_users


EXPECTED_WORKING_HOURS = 8.0


def get_time_report(taxon, start_at, end_at, comment):
    message = ""
    users_to_get_report = [user for user in get_users()]
    if taxon:
        users_to_get_report = [user for user in users_to_get_report if user.in_taxon(taxon)]

    has_any_issues = False
    issues_details = []

    for user in users_to_get_report:
        schedules = get_user_schedules(user.user_id, start_at, end_at)
        logged_times = get_user_logged_times(user.user_id, start_at, end_at)
        issues = _get_report_user_issues(schedules, logged_times)
        if issues:
            has_any_issues = True
            user_string = _get_report_user_string(user, start_at, comment)
            issues_details.append(f"{user_string}\n{issues}")

    if has_any_issues:
        message = f"Reporte para el rango de fechas: [{start_at}, {end_at}]\n"
        message += "".join(issues_details)

    return message


def _get_report_user_issues(schedules, logged_times):
    issues = ""
    for schedule in [x for x in schedules if x.is_working_day]:
        for logged_time in logged_times:
            if schedule.date == logged_time.date and (
                not logged_time.has_logged_time or logged_time.total_hours != EXPECTED_WORKING_HOURS
            ):
                issues += f"  - {schedule.date}: {logged_time.total_hours} horas\n"
    return issues


def _get_report_user_string(user, start_at, comment):
    year, month, _ = start_at.split("-")
    url = f"https://sysdig.bizneohr.com/time-attendance/my-logs/{user.user_id}?date={year}-{month}-01"
    user_info = f"{user.first_name} {user.last_name}: {url}"
    return f"{comment}\n{user_info}" if comment else user_info
