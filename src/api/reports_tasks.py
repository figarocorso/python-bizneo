from src.api.bizneo_requestor import get_user_logged_times, get_user_schedules, get_users


EXPECTED_WORKING_HOURS = 8.0
EXPECTED_HALF_WORKING_HOURS = 4.0


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
    working_dates = {s.date for s in schedules if s.is_working_day}
    logged_by_date = {lt.date: lt for lt in logged_times}

    issue_lines = []
    for date in sorted(working_dates):
        lt = logged_by_date.get(date)
        if lt is None or not lt.has_logged_time:
            issue_lines.append(f"  - {date}: 0 horas (día laboral sin registro)")
            continue
        regular = lt.regular_hours
        if regular >= EXPECTED_WORKING_HOURS or regular == EXPECTED_HALF_WORKING_HOURS:
            continue
        suffix = f" ({lt.project_hours:g}h en proyecto)" if lt.has_projects else ""
        issue_lines.append(f"  - {date}: {regular:g} horas regulares{suffix}")

    for date in sorted(logged_by_date):
        lt = logged_by_date[date]
        if date in working_dates or not lt.has_logged_time:
            continue
        if lt.regular_hours <= 0:
            continue
        suffix = f" ({lt.project_hours:g}h en proyecto)" if lt.has_projects else ""
        issue_lines.append(
            f"  - {date}: {lt.regular_hours:g} horas regulares (día no laboral con registro){suffix}"
        )

    return "\n".join(issue_lines) + "\n" if issue_lines else ""


def _get_report_user_string(user, start_at, comment):
    year, month, _ = start_at.split("-")
    url = f"https://sysdig.bizneohr.com/time-attendance/my-logs/{user.user_id}?date={year}-{month}-01"
    user_info = f"{user.first_name} {user.last_name}: {url}"
    return f"{comment}\n{user_info}" if comment else user_info
