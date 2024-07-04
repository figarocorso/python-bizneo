#!/usr/bin/env python3

import click

from src.absences_tasks import create_absence_for_all_users


@click.group()
def cli():
    pass


@cli.group()
def absences():
    pass


@absences.command()
@click.option("--kind", type=str, required=True, help="Kind of the absence to add")
@click.option("--start_at", type=str, required=True, help="Date of the absence to add")
@click.option("--end_at", type=str, required=True, help="Date of the absence to add")
@click.option("--comment", type=str, required=False, default="", help="Name of the absence to add")
@click.option("--user_id", type=str, help="User to add the absence (empty for all users)")
def add(kind, start_at, end_at, comment, user_id):
    if not user_id:
        create_absence_for_all_users(kind, start_at, end_at, comment)


if __name__ == "__main__":
    cli()
