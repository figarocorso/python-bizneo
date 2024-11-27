#!/usr/bin/env python3
# /// script
# dependencies = [
#   "click<9.0.0,>=8.1.7",
#   "playwright<2.0.0,>=1.45.0",
#   "requests<3.0.0,>=2.32.3",
# ]
# ///

import ast
from datetime import datetime, timedelta
from typing import Literal

import click

from src.api.absences_tasks import create_absence_for_all_users, create_absence_for_user
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


def parse_date_today(ctx, param, value):
    if value:
        value = datetime.strptime(value, "%Y-%m-%d")
    else:
        value = datetime.now()
    return value


@browser.command()
@click.option(
    "--date",
    type=str,
    callback=parse_date_today,
    required=False,
    help="Date in format YYYY-M-D (Default: today)",
)
@click.option("--headless", is_flag=True, required=False, help="Run browser in headless mode")
@click.option(
    "--browser",
    type=click.Choice(["firefox", "chromium"]),
    required=False,
    default="firefox",
    help="What kind of browser should be run: firefox, chromium",
)
def expected(date: str, headless: bool, browser: Literal["firefox", "chromium"]):
    add_expected_schedule(date, headless, browser)


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


if __name__ == "__main__":
    cli()
