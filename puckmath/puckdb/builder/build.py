import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from puckmath.puckdb.builder.utils import *
from puckmath.puckdb.schema import base, team


def build_teams(session):
    """
    Builds the Team objects in the database.
    :param session:
    :return:
    """
    for key, val in TEAMS_ABBREVIATIONS.items():
        session.merge(team.Team(team_abbr=val, team_name=key))

    session.commit()


def create_tables(db_route):
    """
    Creates the table objects
    :param db_route:
    :return:
    """
    engine = create_engine('postgresql://{0}'.format(db_route))

    base.Base.metadata.bind = engine
    base.Base.metadata.create_all(engine)

    insp = inspect(engine)  # will be a PGInspector
    print(insp.get_enums())


def make_session(db_route):
    """
    Create a session for interfacing with the postgres DB.
    :param db_route: user:password@url/puckdb string
    :return: session, engine
    """

    engine = create_engine('postgresql://{0}'.format(db_route))

    base.Base.metadata.bind = engine
    base.Base.metadata.create_all(engine)

    _session = sessionmaker(bind=engine)
    session = _session()

    return session, engine
