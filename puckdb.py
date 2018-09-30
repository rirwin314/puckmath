#!/bin/usr/local/python
import click
import os
from puckmath.config.file import ConfigFile
from puckmath.puckdb.utils.html_report_fetcher import fetch_all_html_reports
from puckmath.puckdb.utils.player_linker import player_linker
from puckmath.puckdb.utils.populate import populate_database
from puckmath.puckdb.utils.create_db import create_db


@click.group()
def cli():
    pass


@cli.command()
def configure():
    print('test')
    if os.path.exists(ConfigFile.FILE_PATH):
        if input('Configuration file already exists; overwrite? [y/n]') != 'y':
            return

    user = input(f"Postgres username [{ConfigFile.get_key('postgres', 'username')}]: ")
    uri = input(f"Postgres URI [{ConfigFile.get_key('postgres', 'uri')}]: ")
    port = input(f"Postgres port [{ConfigFile.get_key('postgres', 'port')}]: ")
    db_name = input(f"Postgres DB name [{ConfigFile.get_key('postgres', 'db_name')}]: ")

    data_directory = input(f"Data directory [{ConfigFile.get_key('local', 'data_directory')}]: ")
    
    if user != '':
        ConfigFile.put_key('postgres', 'username', user)
    if uri != '':
        ConfigFile.put_key('postgres', 'uri', uri)
    if port != '':
        ConfigFile.put_key('postgres', 'port', port)
    if db_name != '':
        ConfigFile.put_key('postgres', 'db_name', db_name)
    if data_directory != '':
        ConfigFile.put_key('local', 'data_directory', data_directory)

    print('Successfully wrote puckdb configuration.')


@cli.command()
@click.option('--start-year', type=click.INT)
@click.option('--end-year', type=click.INT)
@click.option('--ignore-preseason', is_flag=True)
@click.option('--ignore-regular-season', is_flag=True)
@click.option('--ignore-playoffs', is_flag=True)
@click.option('--dest-dir', type=click.STRING)
def fetchhtml(start_year, end_year, ignore_preseason, ignore_regular_season, ignore_playoffs, dest_dir):
    fetch_all_html_reports(start_year, end_year, ignore_preseason, ignore_regular_season, ignore_playoffs, dest_dir)


@cli.command()
def link():
    player_linker()


@cli.command()
@click.option('--start-year', type=click.INT)
@click.option('--end-year', type=click.INT)
@click.option('--start-game', type=click.INT)
@click.option('--end-game', type=click.INT)
@click.option('--ignore-preseason', is_flag=True)
@click.option('--ignore-regular-season', is_flag=True)
@click.option('--ignore-playoffs', is_flag=True)
@click.option('--src-path', type=click.STRING)
def populate(start_year, end_year, start_game, end_game, ignore_preseason, ignore_regular_season, ignore_playoffs, src_path):
    populate_database(start_year, end_year, start_game, end_game, ignore_preseason, ignore_regular_season, ignore_playoffs, src_path)


@cli.command()
def createdb():
    create_db()


if __name__ == '__main__':
    cli()
