from puckmath.puckdb.builder.player_linker import parse_player_info, patch_game_times, link_gpas_to_players_href
from puckmath.puckdb.builder.build import make_session
from puckmath.puckdb.utils.build_db_route import build_db_route


def player_linker():
    db_route = build_db_route()

    session, engine = make_session(db_route)

    print('Patching game times...')
    patch_game_times(session)

    session.commit()
    session.flush()

    print('Parsing player info...')
    parse_player_info(session)

    session.commit()
    session.flush()

    print('Linking GPAs to Players...')
    # link_gpas_to_players(session)
    link_gpas_to_players_href(session)

    session.commit()
    session.flush()
