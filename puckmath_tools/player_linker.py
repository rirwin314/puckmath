import os
import json

from puckmath.core.builder.PlayerLinker import parse_player_info, link_gpas_to_players, patch_game_times, link_gpas_to_players_href
from puckmath.core.builder.build import make_session


if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    db_route = '{}:{}@{}:{}/{}'.format(config['db_conf']['usr'],
                                       config['db_conf']['pwd'],
                                       config['db_conf']['addr'],
                                       config['db_conf']['port'],
                                       config['db_conf']['nm'])

    session, engine = make_session(db_route)

    print('Patching game times...')
    patch_game_times(session)

    session.commit()
    session.flush()

    print('Parsing player info...')
    parse_player_info(session, data_path='E:\\Puckmath_Data')

    session.commit()
    session.flush()

    print('Linking GPAs to Players...')
    # link_gpas_to_players(session)
    link_gpas_to_players_href(session)

    session.commit()
    session.flush()