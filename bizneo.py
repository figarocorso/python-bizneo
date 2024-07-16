#!/usr/bin/env python3

import ast
from datetime import datetime, timedelta

import click

from src.api.absences_tasks import (
    create_absence_for_all_users,
    create_absence_for_user,
    get_time_report_for_taxon,
)
from src.api.webhook import send_message_to_webhook


@click.group()
def cli():
    pass


@cli.group()
def absences():
    pass


@cli.group()
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
@click.option("--taxon", type=str, required=True, help="Needle for a taxon/org name for the report")
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
def report(taxon, start_at, end_at, webhook, headers):
    if not start_at or not end_at:
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        start_at = last_monday.strftime("%Y-%m-%d")
        end_at = last_sunday.strftime("%Y-%m-%d")

    report_text = get_time_report_for_taxon(taxon, start_at, end_at)
    if not webhook:
        print(report_text)
        return

    ok, response = send_message_to_webhook(webhook, report_text, headers)
    if not ok:
        print("There was an error with the webhook request:\n{response}")


if __name__ == "__main__":
    cli()
