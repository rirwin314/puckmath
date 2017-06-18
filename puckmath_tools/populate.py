import argparse
import json

from puckmath.core.builder import build
from puckmath.core.builder.GameFactory import GameFactory
from puckmath.core.schema.Game import Game

if __name__ == '__main__':
    arg = argparse.ArgumentParser()

    arg.add_argument('--config', type=str, default='conf.json')
    arg.add_argument('--start-year', type=int, default=2008)
    arg.add_argument('--end-year', type=int, default=2017)
    arg.add_argument('--ignore-preseason', action='store_true')
    arg.add_argument('--ignore-regular-season', action='store_true')
    arg.add_argument('--ignore-playoffs', action='store_true')

    args = arg.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    db_str = '{}:{}@{}:{}/{}'.format(config['db_conf']['usr'],
                                     config['db_conf']['pwd'],
                                     config['db_conf']['addr'],
                                     config['db_conf']['port'],
                                     config['db_conf']['nm'])
    session, engine = build.make_session(db_str)

    build.build_teams(session)

    start_year = args.start_year
    end_year = args.end_year

    game_types = [1, 2, 3]

    if args.ignore_preseason: game_types.remove(1)
    if args.ignore_regular_season: game_types.remove(2)
    if args.ignore_playoffs: game_types.remove(3)

    src_dir = config['src_dir']

    for year in range(start_year, end_year + 1):
        for game_type in game_types:
            game_num = 1
            while 1:
                print('Working on {0}, {1}-{2}, {3:03d}'.format('Preseason' if game_type == 1 else 'Regular Season',
                                                                year - 1,
                                                                year, game_num))
                game = GameFactory()
                try:
                    if not len(session.query(Game).filter(
                                    Game.game_id == game._build_game_id(year, game_type, game_num)).all()):
                        game.build(session, year, game_type, game_num, src_dir)
                    else:
                        print('Game exists, skipping')
                except FileNotFoundError as e:
                    print(e)
                    if game_type == 2 and game_num < 82 * 31 / 2:
                        game_num += 1
                        continue
                    else:
                        break
                finally:
                    game_num += 1

        # Playoff parsing
        for round in range(1, 5):
            for bracket in range(1, 2 ** (4 - round) + 1):
                for game_num in range(1, 8):
                    game = GameFactory()
                    try:
                        if not len(session.query(Game).filter(Game.game_id == game._build_game_id(year, 3, int(
                                                        100 * round + 10 * bracket + game_num))).all()):
                            game.build(session, year, 3, int(100 * round + 10 * bracket + game_num), src_dir)
                        else:
                            print('Game exists, skipping')
                    except FileNotFoundError:
                        break
        session.commit()
        session.flush()
