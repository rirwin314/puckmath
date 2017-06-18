import os

from puckmath.core.builder.PlayerLinker import parse_player_info, link_gpas_to_players, patch_game_times, link_gpas_to_players_href
from puckmath.core.builder.build import make_session


if __name__ == '__main__':
    puckmath_url = os.environ['PUCKMATH_URL']
    puckmath_usr = os.environ['PUCKMATH_USR']
    puckmath_pwd = os.environ['PUCKMATH_PWD']

    db_route = '{}:{}@{}/puckmath'.format(puckmath_usr, puckmath_pwd, puckmath_url)

    session, engine = make_session(db_route)

    print('Patching game times...')
    patch_game_times(session)

    session.commit()
    session.flush()

    print('Parsing player info...')
    parse_player_info(session, raw_data_dir='E:\\Puckmath_Data')

    session.commit()
    session.flush()

    print('Linking GPAs to Players...')
    # link_gpas_to_players(session)
    link_gpas_to_players_href(session)

    session.commit()
    session.flush()