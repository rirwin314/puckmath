from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, aliased, relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from puckmath.core.schema import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from nhlscrapi.games.game import Game, GameType, GameKey
from nhlscrapi.games.rosters import Rosters
from nhlscrapi.games.playbyplay import PlayByPlay, Play

import logging
import os
import urllib.request
from datetime import datetime, time
from bs4 import BeautifulSoup


def build_players(session):
    from string import ascii_lowercase

    dat_to_add = []
    for c in ascii_lowercase:
        logging.debug('Reading player names "{0}"'.format(c.upper()))

        player_id_fnm = os.path.join('raw_data', 'hr_players_{0}.html'.format(c))

        if not os.path.isfile(player_id_fnm):
            link = 'http://www.hockey-reference.com/players/{0}'.format(c)
            logging.debug('Reading HTML from link: {0}'.format(link))

            try:
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) ' \
                             'Gecko/2009021910 Firefox/3.0.7'
                headers = {'User-Agent': user_agent, }
                request = urllib.request.Request(link, None, headers)  # The assembled request
                response = urllib.request.urlopen(request)
                html = str(response.read())
            except urllib.request.HTTPError:
                continue

            with open(player_id_fnm, 'w') as f:
                f.write(html)
        else:
            with open(player_id_fnm, 'r') as f:
                html = f.read()

        player_dat = html.split('<p class="nhl">')
        for pl in player_dat[1:]:
            try:
                pl_id = pl.split('</p>')[0].split('/players/')[1].split('.html')[0]
            except Exception as e:
                logging.error('Could not get player id from: {0}'.format(pl))
                logging.error(e)
                continue

            try:
                name = pl.split('">')[1].split('<')[0]
            except Exception as e:
                logging.error('Could not get name from: {0}'.format(pl))
                logging.error(e)
                continue

            try:
                min_yr = int((pl.split('(')[1]).split('-')[0])
                max_yr = int((pl.split('(')[1]).split('-')[1].split(',')[0])
            except Exception as e:
                logging.error('Could not get year range from: {0}'.format(pl))
                logging.error(e)
                pos = pl.split('(')[1].split(')')[0]
                min_yr = 'NULL'
                max_yr = 'NULL'
            else:
                pos = pl.split('(')[1].split(',')[1].split(')')[0]

            dat_to_add.append({'player_id': pl_id,
                               'full_name': name,
                               'start_year': min_yr,
                               'last_year': max_yr,
                               'position': pos.strip()})

    for dat in dat_to_add:
        session.merge(Player(**dat))

    session.flush()


def build_games(session):
    for year in range(2002, datetime.now().year+1):

        year_games_fnm = os.path.join('raw_data', 'hr_year_{0}.html'.format(year))
        if not os.path.isfile(year_games_fnm):
            url = 'http://www.hockey-reference.com/leagues/NHL_{0}_games.html'.format(year)
            logging.debug('Reading HTML from link: {0}'.format(url))

            try:
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) ' \
                             'Gecko/2009021910 Firefox/3.0.7'
                headers = {'User-Agent': user_agent, }
                request = urllib.request.Request(url, None, headers)  # The assembled request
                response = urllib.request.urlopen(request)
                html = str(response.read())
            except urllib.request.HTTPError:
                continue

            with open(year_games_fnm, 'w') as f:
                f.write(html)
        else:
            with open(year_games_fnm, 'r') as f:
                html = f.read()

        soup = BeautifulSoup(html)

        t = soup.find('table', {'id': 'games'})
        try:
            rows = t.findAll('tr')
        except AttributeError:
            continue

        data = []
        data_stats = ['game_id', 'home_goals', 'attendance', 'home_team_name', 'away_team_name', 'away_goals',
                      'game_remarks', 'overtimes', 'game_duration']
        data_types = dict(zip(data_stats, [str, int, int, str, str, int, str, str, time]))
        for r in rows[1:]:
            data.append(dict(zip(data_stats, [None]*len(data_stats))))
            h = r.find('th')
            data[-1]['game_id'] = h.attrs['csk']
            for ds in data_stats:
                for td in r.findAll('td', {'data-stat': ds}):
                    if data_types[ds] is str:
                        data[-1][ds] = td.text
                    elif data_types[ds] is int:
                        if not len(td.text):
                            data[-1][ds] = None
                        else:
                            data[-1][ds] = td.text.replace(',', '')
                    elif data_types[ds] is time:
                        if len(td.text.strip()):
                            data[-1][ds] = time(*[int(d) for d in td.text.split(':')])
                        else:
                            data[-1][ds] = None

        for dat in data:
            session.merge(Game(**dat))

    session.flush()


def _team_abbreviation(tmnm):
    teams_by_abbr = {
        'ANAHEIM DUCKS': 'ANA',
        'ARIZONA COYOTES': 'ARI',
        'ATLANTA THRASHERS': 'ATL',
        'ATLANTA FLAMES': 'ATLF',
        'BOSTON BRUINS': 'BOS',
        'BROOKLYN AMERICANS': 'BRK',
        'BUFFALO SABRES': 'BUF',
        'CALIFORNIA GOLDEN SEALS': 'CAL',
        'CAROLINA HURRICANES': 'CAR',
        'CALGARY FLAMES': 'CGY',
        'CHICAGO BLACKHAWKS': 'CHI',
        'COLUMBUS BLUE JACKETS': 'CBJ',
        'CLEVELAND BARONS': 'CLE',
        'COLORADO AVALANCHE': 'COL',
        'COLORADO ROCKIES': 'COLR',
        'DALLAS STARS': 'DAL',
        'DETROIT RED WINGS': 'DET',
        'EDMONTON OILERS': 'EDM',
        'FLORIDA PANTHERS': 'FLA',
        'HAMILTON TIGERS': 'HAM',
        'HARTFORD WHALERS': 'HAR',
        'KANSAS CITY SCOUTS': 'KC',
        'LOS ANGELES KINGS': 'LAK',
        'MIGHTY DUCKS OF ANAHEIM': 'MDA',
        'MINNESOTA WILD': 'MIN',
        'MINNESOTA NORTH STARS': 'MNS',
        'MONTREAL CANADIENS': 'MTL',
        'MONTREAL MAROONS': 'MTLM',
        'MONTREAL WANDERERS': 'MTLW',
        'NASHVILLE PREDATORS': 'NSH',
        'NEW JERSEY DEVILS': 'NJD',
        'NEW YORK AMERICANS': 'NYA',
        'NEW YORK ISLANDERS': 'NYI',
        'NEW YORK RANGERS': 'NYR',
        'OAKLAND SEALS': 'OAK',
        'OTTAWA SENATORS': 'OTT',
        'OTTAWA SENATORS (ORIGINAL)': 'OTTO',
        'PHILADELPHIA FLYERS': 'PHI',
        'PHILADELPHIA QUAKERS': 'PHIQ',
        'PHOENIX COYOTES': 'PHX',
        'PITTSBURGH PENGUINS': 'PIT',
        'PITTSBURGH PIRATES': 'PITP',
        'QUEBEC NORDIQUES': 'QUE',
        'QUEBEC BULLDOGS': 'QUEB',
        'SAN JOSE SHARKS': 'SJS',
        'ST. LOUIS BLUES': 'STL',
        'ST LOUIS BLUES': 'STL',
        'ST. LOUIS EAGLES': 'STLE',
        'TAMPA BAY LIGHTNING': 'TBL',
        'TORONTO MAPLE LEAFS': 'TOR',
        'VANCOUVER CANUCKS': 'VAN',
        'WASHINGTON CAPITALS': 'WSH',
        'WINNIPEG JETS': 'WPG',
        'WINNIPEG JETS (ORIGINAL)': 'WPGO'
    }

    tmnm = tmnm.replace("b'", '')

    for team_name in teams_by_abbr:
        if team_name.upper() == tmnm:
            return teams_by_abbr[team_name]

    raise 'Cannot match team name {0}'.format(tmnm)


def _scrapi_game_to_game_id(game):
    home_abbr = _team_abbreviation(game.matchup['home'].replace("b'", ''))
    dt = datetime.strptime(game.matchup['date'].replace("b'", ''), '%A, %B %d, %Y')
    return dt.strftime('%Y%m%d0')+home_abbr


def _build_roster(session, game_key):
    def _player_name_to_id(player_name):
        player_name = player_name.replace("'", "\\'")
        pls = session.query(Player).filter(
            Player.full_name.ilike('%{0}%'.format(player_name.lower()))
        ).all()

        if len(pls) == 1:
            return pls[0].player_id

        player_name = ''.join([c for c in player_name if c == ' ' or c.isalnum()])
        first_name = player_name.split(' ')[0]
        last_name = ''.join(player_name.split(' ')[1:])
        pl_id = '{0}{1}'.format(last_name[:min([5, len(last_name)])], first_name[:1])

        pls = session.query(Player).filter(
            Player.player_id.ilike('%{0}%'.format(pl_id.lower()))).filter(
            Player.start_year <= game_key.season).filter(
            Player.last_year >= game_key.season).all()

        if len(pls):
            return pls[0].player_id
        else:
            return None

    rosters = Rosters(game_key=game_key)
    game_id = _scrapi_game_to_game_id(rosters)
    print(rosters.matchup)
    print('Game id: {0}'.format(game_id))

    _game = session.query(Game).filter(Game.game_id == game_id).first()
    _game.home_coach = rosters.home_coach
    _game.away_coach = rosters.away_coach

    _rosters = []
    _rosters += [Roster(team_name=rosters.matchup['home'], jersey_num=j, game_id=game_id,
                        player_id=_player_name_to_id(rosters.home_skaters[j]['name']),
                        position=rosters.home_skaters[j]['position']) for j in rosters.home_skaters]
    _rosters += [Roster(team_name=rosters.matchup['away'], jersey_num=j, game_id=game_id,
                        player_id=_player_name_to_id(rosters.away_skaters[j]['name']),
                        position=rosters.away_skaters[j]['position']) for j in rosters.away_skaters]

    _scratches = []
    _scratches += [Scratch(team_name=rosters.matchup['home'], jersey_num=j, game_id=game_id,
                           player_id=_player_name_to_id(rosters.home_scratches[j]['name']),
                           position=rosters.home_scratches[j]['position']) for j in rosters.home_scratches]
    _scratches += [Scratch(team_name=rosters.matchup['away'], jersey_noum=j, game_id=game_id,
                           player_id=_player_name_to_id(rosters.away_scratches[j]['name']),
                           position=rosters.away_scratches[j]['position']) for j in rosters.away_scratches]

    session.add(_game)
    session.add_all(_rosters)
    session.add_all(_scratches)


def build_rosters(session):
    for year in range(2008, 2018):
        game_num = 1
        while 1:
            game_key = GameKey(year, GameType.Regular, game_num)

            game = Game(game_key)

            if game.away_coach is None:
                break

            print('Working game {0}'.format(game_key.to_tuple()))

            _build_roster(session, game_key)

            game_num += 1

    session.commit()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Database builder')
    parser.add_argument('--build-players', action='store_true')
    parser.add_argument('--build-games', action='store_true')
    parser.add_argument('--build-rosters', action='store_true')

    args = parser.parse_args()

    db_fnm = os.path.join(os.getcwd(), 'databases', 'puckmath.db')

    engine = create_engine('sqlite:///{0}'.format(db_fnm))

    schema.Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if args.build_players:
            build_players(session)
        if args.build_games:
            build_games(session)
        if args.build_rosters:
            build_rosters(session)
    except Exception as e:
        print(e)
    finally:
        session.commit()

    return session, engine


if __name__ == '__main__':
    session, engine = main()