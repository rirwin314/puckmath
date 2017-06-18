import os

from puckmath.config.file import ConfigFile
from puckmath.puckdb.builder import build
from puckmath.puckdb.builder.game_factory import GameFactory
from puckmath.puckdb.schema.game import Game
from puckmath.puckdb.utils.build_db_route import build_db_route


GAMES_PER_SEASON = 82
NUMBER_OF_TEAMS = 31


def populate_database(start_year, end_year, start_game, end_game, ignore_preseason, ignore_regular_season, ignore_playoffs, src_path):
    db_route = build_db_route()

    session, engine = build.make_session(db_route)

    build.build_teams(session)

    game_types = [1, 2, 3]

    if ignore_preseason:
        game_types.remove(1)
    if ignore_regular_season:
        game_types.remove(2)
    if ignore_playoffs:
        game_types.remove(3)

    if src_path is None:
        src_path = os.path.join(ConfigFile.get_key('local', 'data_directory'), 'nhl')

    for year in range(start_year, end_year + 1):
        if start_game is None or end_game is None:
            for game_type in game_types:
                game_num = 1
                while 1:
                    print('Working on {0}, {1}-{2}, {3:03d}'.format('Preseason' if game_type == 1 else 'Regular Season',
                                                                    year - 1,
                                                                    year, game_num))
                    game = GameFactory()
                    try:
                        if not len(session.query(Game).filter(
                                Game.game_id == game.build_game_id(year, game_type, game_num)).all()):
                            game.build(session, year, game_type, game_num, src_path)
                        else:
                            print('Game exists, skipping')
                    except FileNotFoundError as e:
                        print(e)
                        if game_type == 2 and game_num < NUMBER_OF_TEAMS * GAMES_PER_SEASON // 2 + 1:
                            game_num += 1
                            continue
                        else:
                            break
                    except Exception as e:
                        print(e)
                        game_num += 1
                    finally:
                        game_num += 1

            # Playoff parsing
            for playoff_round in range(1, 5):
                for bracket in range(1, 2 ** (4 - playoff_round) + 1):
                    for game_num in range(1, 8):
                        game = GameFactory()
                        try:
                            if not len(session.query(Game).filter(Game.game_id == game.build_game_id(year, 3, int(
                                    100 * playoff_round + 10 * bracket + game_num))).all()):
                                game.build(session, year, 3, int(100 * playoff_round + 10 * bracket + game_num),
                                           src_path)
                            else:
                                print('Game exists, skipping')
                        except FileNotFoundError:
                            break
        else:
            game_type = 2
            for game_num in range(start_game, end_game + 1):
                print('Working on {0}, {1}-{2}, {3:03d}'.format('Preseason' if game_type == 1 else 'Regular Season',
                                                                year - 1,
                                                                year, game_num))
                game = GameFactory()
                try:
                    if not len(session.query(Game).filter(
                            Game.game_id == game.build_game_id(year, game_type, game_num)).all()):
                        game.build(session, year, game_type, game_num, src_path)
                    else:
                        print('Game exists, skipping')
                except FileNotFoundError as e:
                    print(e)

        session.commit()
        session.flush()
