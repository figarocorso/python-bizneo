#!/usr/bin/env python3

import ast
from datetime import datetime, timedelta
from typing import Literal

import click

from src.api.absences_tasks import create_absence_for_all_users, create_absence_for_user
from src.api.bizneo_requestor import get_user, get_users, update_user_slack_id
from src.api.reports_tasks import get_time_report
from src.api.webhook import send_message_to_webhook
from src.browser.library import add_expected_schedule, login_into


@click.group()
def cli():
    pass


@cli.group()
def admin():
    pass


@cli.group()
def browser():
    pass


@admin.group()
def absences():
    pass


@admin.group()
def time():
    pass


@admin.group()
def users():
    pass


@absences.command()
@click.option("--kind", type=str, required=True, help="Kind of the absence to add")
@click.option("--start_at", type=str, required=True, help="Date of the absence to add")
@click.option("--end_at", type=str, required=True, help="Date of the absence to add")
@click.option("--comment", type=str, required=False, default="", help="Name of the absence to add")
@click.option("--user_id", type=str, help="User to add the absence (empty for all users)")
def add(kind, start_at, end_at, comment, user_id):
    if user_id:
        create_absence_for_user(user_id, kind, start_at, end_at, comment)
    else:
        create_absence_for_all_users(kind, start_at, end_at, comment)


def parse_dict(ctx, param, value):
    if not value:
        return value

    try:
        return ast.literal_eval(value)
    except Exception:
        raise click.BadParameter("Value must be a dictionary")


@time.command()
@click.option(
    "--taxon",
    type=str,
    required=False,
    default="",
    help="Needle for a taxon/org name for the report (empty for all users)",
)
@click.option("--start_at", type=str, required=False, help="Start date for the report (empty for last week)")
@click.option("--end_at", type=str, required=False, help="End date for the report (empty for last week)")
@click.option(
    "--webhook",
    type=str,
    required=False,
    help="URL to send the report through POST request (empty for console output)",
)
@click.option(
    "--headers",
    type=str,
    callback=parse_dict,
    required=False,
    help="Dict containing the headers to add to the request",
)
@click.option("--comment", type=str, default="", required=False, help="Customize first line output")
def report(taxon, start_at, end_at, webhook, headers, comment):
    if not start_at or not end_at:
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_at = last_monday.strftime("%Y-%m-%d")
        end_at = last_sunday.strftime("%Y-%m-%d")

    report_text = get_time_report(taxon, start_at, end_at, comment)
    if not webhook:
        print(report_text)
        return

    ok, response = send_message_to_webhook(webhook, report_text, headers)
    if not ok:
        print("There was an error with the webhook request:\n{response}")


@time.command()
@click.option("--comment", type=str, default="", required=False, help="Customize first line output")
@click.option("--start_at", type=str, required=False, help="Start date for the report (empty for last week)")
@click.option("--end_at", type=str, required=False, help="End date for the report (empty for last week)")
@click.option(
    "--webhook",
    type=str,
    required=True,
    help="URL to send the report through POST request",
)
@click.option(
    "--headers",
    type=str,
    callback=parse_dict,
    required=False,
    help="Dict containing base headers (channel-id will be overridden per user)",
)
@click.option(
    "--taxon",
    type=str,
    required=False,
    default="",
    help="Filter users by taxon/org name (empty for all users)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    required=False,
    help="Print reports to console instead of sending to webhook",
)
def individual_reports(comment, start_at, end_at, webhook, headers, taxon, dry_run):
    """Send individual time reports to each user's Slack channel."""
    if not start_at or not end_at:
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_at = last_monday.strftime("%Y-%m-%d")
        end_at = last_sunday.strftime("%Y-%m-%d")

    # Get all users (list endpoint doesn't include slack_id)
    all_users_list = get_users()
    users_to_report = (
        all_users_list if not taxon else [user for user in all_users_list if user.in_taxon(taxon)]
    )

    click.echo(f"Fetching full user details for {len(users_to_report)} users...")

    # Fetch full user details to get slack_id
    users_with_slack = []
    users_without_slack = []
    for user_basic in users_to_report:
        user_full = get_user(user_basic.user_id)
        if user_full.slack_id:
            users_with_slack.append(user_full)
        else:
            users_without_slack.append(user_full)

    if not users_with_slack:
        click.echo(f"No users with Slack ID found{f' for taxon: {taxon}' if taxon else ''}")
        return

    click.echo(f"Sending individual reports to {len(users_with_slack)} users...")
    click.echo(f"Date range: [{start_at}, {end_at}]")
    click.echo(f"Dry-run mode: {'ON' if dry_run else 'OFF'}\n")

    success_count = 0
    skip_count = 0
    error_no_slack_count = 0

    for user in users_with_slack:
        # Generate individual report for this user using the same logic as test_single_user
        from src.api.bizneo_requestor import get_user_schedules, get_user_logged_times
        from src.api.reports_tasks import _get_report_user_issues, _get_report_user_string

        schedules = get_user_schedules(user.user_id, start_at, end_at)
        logged_times = get_user_logged_times(user.user_id, start_at, end_at)
        issues = _get_report_user_issues(schedules, logged_times)

        # Check if user has issues to report
        if not issues:
            skip_count += 1
            click.echo(f"⏭️  Skipping {user.first_name} {user.last_name} - no issues")
            continue

        # Build the report with issues
        user_string = _get_report_user_string(user, start_at, "")
        if comment:
            user_report = (
                f"{comment}\nReporte para el rango de fechas: [{start_at}, {end_at}]\n{user_string}\n{issues}"
            )
        else:
            user_report = f"Reporte para el rango de fechas: [{start_at}, {end_at}]\n{user_string}\n{issues}"

        # Prepare headers with user's slack channel
        user_headers = headers.copy() if headers else {}
        user_headers["channel-id"] = user.slack_id

        if dry_run:
            click.echo(f"\n{'='*60}")
            click.echo(f"DRY-RUN: Would send to {user.first_name} {user.last_name}")
            click.echo(f"Slack ID: {user.slack_id}")
            click.echo(f"Webhook: {webhook}")
            click.echo(f"Headers: {user_headers}")
            click.echo(f"\nReport content:\n{user_report}")
            click.echo(f"{'='*60}\n")
            success_count += 1
        else:
            ok, response = send_message_to_webhook(webhook, user_report, user_headers)
            if ok:
                click.echo(f"✅ Sent to {user.first_name} {user.last_name} ({user.slack_id})")
                success_count += 1
            else:
                click.echo(f"❌ Error sending to {user.first_name} {user.last_name}: {response}")

    # Check for users without Slack ID who have time issues
    for user in users_without_slack:
        schedules = get_user_schedules(user.user_id, start_at, end_at)
        logged_times = get_user_logged_times(user.user_id, start_at, end_at)
        issues = _get_report_user_issues(schedules, logged_times)
        if issues:
            error_no_slack_count += 1
            click.echo(
                f"⚠️  ERROR: {user.first_name} {user.last_name} ({user.email}) has time issues but NO Slack ID configured!"
            )

    click.echo(f"\n{'Dry-run' if dry_run else 'Sending'} completed:")
    click.echo(f"  - Sent: {success_count}")
    click.echo(f"  - Skipped (no issues): {skip_count}")
    click.echo(f"  - Errors (no Slack ID but has issues): {error_no_slack_count}")
    click.echo(f"  - Total users with Slack ID: {len(users_with_slack)}")
    click.echo(f"  - Total users without Slack ID: {len(users_without_slack)}")


@time.command()
@click.option("--email", type=str, required=True, help="Email of the user to send the report to")
@click.option("--comment", type=str, default="", required=False, help="Customize first line output")
@click.option("--start_at", type=str, required=False, help="Start date for the report (empty for last week)")
@click.option("--end_at", type=str, required=False, help="End date for the report (empty for last week)")
@click.option(
    "--webhook",
    type=str,
    required=True,
    help="URL to send the report through POST request",
)
@click.option(
    "--dry-run",
    is_flag=True,
    required=False,
    help="Print report to console instead of sending to webhook",
)
def test_single_user(email, comment, start_at, end_at, webhook, dry_run):
    """Send time report to a single user via Slack (for testing webhook integration)."""
    if not start_at or not end_at:
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_at = last_monday.strftime("%Y-%m-%d")
        end_at = last_sunday.strftime("%Y-%m-%d")

    # Find user by email
    all_users = get_users()
    user_basic = next((u for u in all_users if u.email == email), None)

    if not user_basic:
        click.echo(f"❌ Error: User with email '{email}' not found")
        return

    # Get full user details to retrieve slack_id
    user = get_user(user_basic.user_id)

    if not user.slack_id:
        click.echo(f"❌ Error: User {user.first_name} {user.last_name} has no Slack ID configured")
        click.echo(
            f"Use 'bizneo admin users update-slack --email {email} --slack-id <SLACK_ID>' to configure it"
        )
        return

    # Generate report for this specific user
    from src.api.bizneo_requestor import get_user_schedules, get_user_logged_times

    schedules = get_user_schedules(user.user_id, start_at, end_at)
    logged_times = get_user_logged_times(user.user_id, start_at, end_at)

    # Check for time issues
    from src.api.reports_tasks import _get_report_user_issues, _get_report_user_string

    issues = _get_report_user_issues(schedules, logged_times)
    user_report = ""

    if issues:
        user_string = _get_report_user_string(user, start_at, "")  # Don't pass comment to avoid duplication
        if comment:
            user_report = (
                f"{comment}\nReporte para el rango de fechas: [{start_at}, {end_at}]\n{user_string}\n{issues}"
            )
        else:
            user_report = f"Reporte para el rango de fechas: [{start_at}, {end_at}]\n{user_string}\n{issues}"

    has_issues = bool(issues)

    click.echo(f"User: {user.first_name} {user.last_name}")
    click.echo(f"Email: {user.email}")
    click.echo(f"Slack ID: {user.slack_id}")
    click.echo(f"Date range: [{start_at}, {end_at}]")
    click.echo(f"Has time issues: {'Yes' if has_issues else 'No'}")
    click.echo(f"Dry-run mode: {'ON' if dry_run else 'OFF'}\n")

    if dry_run:
        click.echo(f"{'='*60}")
        click.echo(f"DRY-RUN: Would send to {user.first_name} {user.last_name}")
        click.echo(f"Webhook: {webhook}")
        click.echo(f"\nReport content:\n{user_report}")
        click.echo(f"{'='*60}\n")
    else:
        # Prepare headers with user's slack channel
        headers = {"channel-id": user.slack_id}

        ok, response = send_message_to_webhook(webhook, user_report, headers)
        if ok:
            click.echo(f"✅ Successfully sent report to {user.first_name} {user.last_name}")
            click.echo(f"Response: {response}")
        else:
            click.echo(f"❌ Error sending report: {response}")


def parse_date_today(ctx, param, value):
    if value:
        value = datetime.strptime(value, "%Y-%m-%d")
    else:
        value = datetime.now()
    return value


@browser.command()
@click.option("--headless", is_flag=True, required=False, help="Run browser in headless mode")
@click.option(
    "--browser",
    type=click.Choice(["firefox", "chromium"]),
    required=False,
    default="firefox",
    help="What kind of browser should be run: firefox, chromium",
)
def expected(headless: bool, browser: Literal["firefox", "chromium"]):
    add_expected_schedule(headless, browser)


@browser.command()
@click.option(
    "--browser",
    type=click.Choice(["firefox", "chromium"]),
    required=False,
    default="firefox",
    help="What kind of browser should be run: firefox, chromium",
)
def login(browser: Literal["firefox", "chromium"]):
    login_into(browser)


@users.command()
@click.option(
    "--taxon",
    type=str,
    required=False,
    default="",
    help="Filter users by taxon/org name (empty for all users)",
)
def list(taxon):
    """List all users or filter by taxon."""
    all_users = get_users()
    users_to_display = all_users if not taxon else [user for user in all_users if user.in_taxon(taxon)]

    if not users_to_display:
        if taxon:
            click.echo(f"No users found for taxon: {taxon}")
        else:
            click.echo("No users found")
        return

    click.echo(f"Found {len(users_to_display)} user(s):\n")
    for user in users_to_display:
        click.echo(f"ID: {user.user_id}")
        click.echo(f"Name: {user.first_name} {user.last_name}")
        click.echo(f"Email: {user.email}")
        click.echo(f"Taxons: {user.main_taxons or 'N/A'}")
        click.echo(f"Slack ID: {user.slack_id or 'N/A'}")
        click.echo("-" * 50)


@users.command()
@click.option("--email", type=str, required=True, help="Email of the user to update")
@click.option("--slack-id", type=str, required=True, help="Slack ID to assign to the user")
def update_slack(email, slack_id):
    """Update Slack ID for a user identified by email."""
    all_users = get_users()
    user = next((u for u in all_users if u.email == email), None)

    if not user:
        click.echo(f"Error: User with email '{email}' not found")
        return

    click.echo(f"Found user: {user.first_name} {user.last_name} (ID: {user.user_id})")
    click.echo(f"Current Slack ID: {user.slack_id or 'N/A'}")
    click.echo(f"New Slack ID: {slack_id}")

    try:
        update_user_slack_id(user.user_id, slack_id)
        click.echo("✅ Slack ID updated successfully!")

        # Verify the update
        updated_user = get_user(user.user_id)
        click.echo(f"\nVerification - Updated Slack ID: {updated_user.slack_id or 'N/A'}")
    except Exception as e:
        click.echo(f"❌ Error updating Slack ID: {e}")


if __name__ == "__main__":
    cli()
