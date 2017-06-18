import json

import puckmath.core.builder.build

if __name__ == '__main__':
    with open('config.json', 'r') as f:
        config = json.load(f)

    db_route = '{}:{}@{}:{}/{}'.format(config['db_conf']['usr'],
                                       config['db_conf']['pwd'],
                                       config['db_conf']['addr'],
                                       config['db_conf']['port'],
                                       config['db_conf']['nm'])

    puckmath.core.builder.build.create_tables(db_route)
    session, engine = puckmath.core.builder.build.make_session(db_route)
    puckmath.core.builder.build.build_teams(session)
