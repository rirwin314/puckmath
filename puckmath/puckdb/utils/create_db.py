from puckmath.puckdb.builder.build import create_tables, build_teams, make_session
from puckmath.puckdb.utils.build_db_route import build_db_route


def create_db():
    db_route = build_db_route()

    create_tables(db_route)
    session, engine = make_session(db_route)
    build_teams(session)
