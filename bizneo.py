#!/usr/bin/env python3

import ast
from datetime import datetime, timedelta
from typing import Literal

import click

from src.api.absences_tasks import create_absence_for_all_users, create_absence_for_user
from src.api.bizneo_requestor import get_users
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


if __name__ == "__main__":
    cli()
