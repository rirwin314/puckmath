from puckmath.core.tools.NHLParser.utils import html_rep


def downloader(_args):
    """
    Download HTML files.
    :param _args:
    :return:
    """
    import argparse

    arg = argparse.ArgumentParser()

    arg.add_argument('--src-dir', type=str, default='.')
    arg.add_argument('--start-year', type=int, default=2008)
    arg.add_argument('--end-year', type=int, default=2017)
    arg.add_argument('--ignore-preseason', action='store_true')
    arg.add_argument('--ignore-regular-season', action='store_true')
    arg.add_argument('--ignore-playoffs', action='store_true')

    args = arg.parse_args(_args)

    years = range(args.start_year, args.end_year+1)

    games_in_a_row = 0

    for year in years:
        # Preseason
        if not args.ignore_preseason:
            game_num = 1
            while 1:
                response = html_rep(year, 1, game_num, 'RO', src_dir=args.src_dir)
                response = html_rep(year, 1, game_num, 'PL', src_dir=args.src_dir)
                response = html_rep(year, 1, game_num, 'TH', src_dir=args.src_dir)
                response = html_rep(year, 1, game_num, 'TV', src_dir=args.src_dir)

                if response is None:
                    games_in_a_row += 1
                    if games_in_a_row > 20:
                        games_in_a_row = 0
                        break

                game_num += 1

        # Regular season games
        if not args.ignore_regular_season:
            game_num = 1
            while 1:
                response = html_rep(year, 2, game_num, 'RO', src_dir=args.src_dir)
                response = html_rep(year, 2, game_num, 'PL', src_dir=args.src_dir)
                response = html_rep(year, 2, game_num, 'TH', src_dir=args.src_dir)
                response = html_rep(year, 2, game_num, 'TV', src_dir=args.src_dir)

                if response is None:
                    games_in_a_row += 1
                    if games_in_a_row > 20:
                        games_in_a_row = 0
                        break

                game_num += 1

        # Playoff games
        if not args.ignore_playoffs:
            round_num = 1
            bracket_num = 1
            game_itr = 1
            while 1:
                game_num = int('{0}{1}{2}'.format(round_num, bracket_num, game_itr))
                response = html_rep(year, 3, game_num, 'RO', src_dir=args.src_dir)
                response = html_rep(year, 3, game_num, 'PL', src_dir=args.src_dir)
                response = html_rep(year, 3, game_num, 'TH', src_dir=args.src_dir)
                response = html_rep(year, 3, game_num, 'TV', src_dir=args.src_dir)

                if response is None:
                    game_itr = 1
                    bracket_num += 1
                    if bracket_num > 2**(4-round_num):
                        round_num += 1
                        bracket_num = 1
                    if round_num > 4:
                        break
                else:
                    game_itr += 1