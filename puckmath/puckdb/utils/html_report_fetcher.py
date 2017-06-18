import eventlet

from tqdm import tqdm
from puckmath.puckdb.nhl_parser.utils import html_rep


NUM_PRESEASON_GAMES = 125
NUM_TEAMS = 31
NUM_GAMES_PER_TEAM = 82

NUM_PLAYOFF_ROUNDS = 4
NUM_GAMES_PER_PLAYOFF_ROUND = 7


def _fetch(args):
    try:
        return html_rep(args[0], args[1], args[2], args[3]), args
    except:
        return None, args


def fetch_all_html_reports(start_year, end_year, ignore_preseason, ignore_regular_season, ignore_playoffs, src_dir):
    """
    Download HTML report files.
    :param start_year:
    :param end_year:
    :param ignore_preseason:
    :param ignore_regular_season:
    :param ignore_playoffs:
    :param src_dir:
    :return:
    """
    years = range(start_year, end_year+1)

    all_args = []
    for year in years:
        # Preseason
        if not ignore_preseason:
            for game_num in range(1, NUM_PRESEASON_GAMES + 1):
                all_args.append((year, 1, game_num, 'RO', src_dir))
                all_args.append((year, 1, game_num, 'PL', src_dir))
                all_args.append((year, 1, game_num, 'TH', src_dir))
                all_args.append((year, 1, game_num, 'TV', src_dir))

        # Regular season games
        if not ignore_regular_season:
            for game_num in range(1, NUM_TEAMS * NUM_GAMES_PER_TEAM // 2 + 1):
                all_args.append((year, 2, game_num, 'RO', src_dir))
                all_args.append((year, 2, game_num, 'PL', src_dir))
                all_args.append((year, 2, game_num, 'TH', src_dir))
                all_args.append((year, 2, game_num, 'TV', src_dir))

        # Playoff games
        if not ignore_playoffs:
            for round_num in range(1, NUM_PLAYOFF_ROUNDS + 1):
                for bracket_num in range(1, 2 ** (4 - round_num) + 1):
                    for game_itr in range(1, NUM_GAMES_PER_PLAYOFF_ROUND + 1):
                        game_num = int('{0}{1}{2}'.format(round_num, bracket_num, game_itr))
                        all_args.append((year, 3, game_num, 'RO', src_dir))
                        all_args.append((year, 3, game_num, 'PL', src_dir))
                        all_args.append((year, 3, game_num, 'TH', src_dir))
                        all_args.append((year, 3, game_num, 'TV', src_dir))

    pool = eventlet.GreenPool()
    for response, args in tqdm(pool.imap(_fetch, all_args)):
        pass
