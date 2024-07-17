from src.api.bizneo_requestor import get_user_logged_times, get_user_schedules, get_users


EXPECTED_WORKING_HOURS = 8.0


def get_time_report_for_taxon(taxon, start_at, end_at):
    message = f"Report for date range: [{start_at}, {end_at}]\n"
    users_in_taxon = [user for user in get_users() if user.in_taxon(taxon)]
    for user in users_in_taxon:
        schedules = get_user_schedules(user.user_id, start_at, end_at)
        logged_times = get_user_logged_times(user.user_id, start_at, end_at)
        issues = _get_report_user_issues(schedules, logged_times)
        if issues:
            user_string = _get_report_user_string(user, start_at)
            message += f"{user_string}\n{issues}"

    return message


def _get_report_user_issues(schedules, logged_times):
    issues = ""
    for schedule in [x for x in schedules if x.is_working_day]:
        for logged_time in logged_times:
            if schedule.date == logged_time.date and (
                not logged_time.has_logged_time or logged_time.total_hours != EXPECTED_WORKING_HOURS
            ):
                issues += f"  - {schedule.date}: {logged_time.total_hours} hours\n"
    return issues


def _get_report_user_string(user, start_at):
    year, month, _ = start_at.split("-")
    url = f"https://sysdig.bizneohr.com/time-attendance/my-logs/{user.user_id}?year={year}&month={month}"
    return f"{user.first_name} {user.last_name}: {url}"
