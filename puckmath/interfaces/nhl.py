import os
import time
import logging
import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup

from puckmath.interfaces.utils import download_html


DATA_DIRECTORY = os.environ.get_key('PUCKMATH_DATA_DIRECTORY', '/tmp/data')

team_map = {
    'ANA': 'ANAHEIM DUCKS',
    'ARI': 'ARIZONA COYOTES',
    'BOS': 'BOSTON BRUINS',
    'BUF': 'BUFFALO SABRES',
    'CAR': 'CAROLINA HURRICANES',
    'CGY': 'CALGARY FLAMES',
    'CHI': 'CHICAGO BLACKHAWKS',
    'CBJ': 'COLUMBUS BLUE JACKETS',
    'COL': 'COLORADO AVALANCHE',
    'DAL': 'DALLAS STARS',
    'DET': 'DETROIT RED WINGS',
    'EDM': 'EDMONTON OILERS',
    'FLA': 'FLORIDA PANTHERS',
    'L.A': 'LOS ANGELES KINGS',
    'MIN': 'MINNESOTA WILD',
    'MTL': 'MONTREAL CANADIENS',
    'NSH': 'NASHVILLE PREDATORS',
    'N.J': 'NEW JERSEY DEVILS',
    'NYI': 'NEW YORK ISLANDERS',
    'NYR': 'NEW YORK RANGERS',
    'OTT': 'OTTAWA SENATORS',
    'PHI': 'PHILADELPHIA FLYERS',
    'PIT': 'PITTSBURGH PENGUINS',
    'S.J': 'SAN JOSE SHARKS',
    'STL': 'ST. LOUIS BLUES',
    'T.B': 'TAMPA BAY LIGHTNING',
    'TOR': 'TORONTO MAPLE LEAFS',
    'VAN': 'VANCOUVER CANUCKS',
    'VGK': 'VEGAS GOLDEN KNIGHTS',
    'WSH': 'WASHINGTON CAPITALS',
    'WPG': 'WINNIPEG JETS'
}

reverse_team_map = {v: k for k, v in team_map.items()}


def logger():
    return logging.getLogger('nhl')


class HtmlReports(object):
    season_types = {'preseason': 1, 'regular': 2, 'playoffs': 3}
    report_types = ['ES', 'FC', 'GS', 'PL', 'RO', 'SS', 'TH', 'TV']
    last_downloaded = None
    desired_delay = 10

    def __init__(self):
        raise RuntimeError('LineCombinations should not be instantiated')

    @staticmethod
    def _download_html(url, file_path):
        """
        Wrapper to prevent downloading too frequently
        :param url:
        :param file_path:
        :return:
        """
        if HtmlReports.last_downloaded is None:
            time_diff = HtmlReports.desired_delay + 1
        else:
            time_diff = (datetime.now() - HtmlReports.last_downloaded).seconds
        if time_diff < HtmlReports.desired_delay:
            logger().info('Waiting for HockeyRef HTML request ({0} seconds)')
            time.sleep(HtmlReports.desired_delay - time_diff)

        download_html(url, file_path)
        HtmlReports.last_downloaded = datetime.now()

    @staticmethod
    def _database(report_type, year, season_type, game_number):
        """

        :param abbr:
        :param gametype:
        :param strength:
        :return:
        """
        assert report_type in HtmlReports.report_types
        if type(year) is str:
            year = int(year[:4])
        if season_type in [k for k in HtmlReports.season_types]:
            season_type = HtmlReports.season_types[season_type]

        file_path = os.path.join(DATA_DIRECTORY, 'nhl', '{0}{1}/{2}/{2}{3:02d}{4:04d}.html'.format(
            year, year + 1, report_type, season_type, game_number))
        html_url_postfix = '{0}{1}/{2}{3:02d}{4:04d}.HTM'.format(year, year + 1, report_type, season_type, game_number)

        if os.path.exists(file_path):
            return file_path

        url = 'http://www.nhl.com/scores/htmlreports/{0}'.format(html_url_postfix)
        HtmlReports._download_html(url, file_path)

        return file_path

    @staticmethod
    def _parse_report(soup):
        """

        :param html_text:
        :return:
        """
        tables = pd.read_html(str(soup).replace('\n', '').replace('\t', ''))
        return tables

    @staticmethod
    def _load_html_soup(file_path):
        with open(file_path, 'r') as f:
            string_data = f.read().replace('\xa0', ' ').replace('<br>', ' ')

        soup = BeautifulSoup(string_data, 'html.parser')
        return soup

    @staticmethod
    def read_report(report_type, year, season_type, game_number):
        file_path = HtmlReports._database(report_type, year, season_type, game_number)

        soup = HtmlReports._load_html_soup(file_path)

        if report_type == 'PL':
            return HtmlReports._filter_play_by_play(soup)

        return HtmlReports._parse_report(soup)

    @staticmethod
    def _filter_play_by_play(soup):
        cols = [c.text for c in soup.find_all('td', attrs={'class': 'heading + bborder'})][:8]
        rows = soup.find_all('tr', attrs={'class': 'evenColor'})

        def parse_players_on_ice_table(table):
            sub_tables = table.find_all('table')
            names = [t.find('font')['title'] for t in sub_tables]
            numbers = [t.find('font').text for t in sub_tables]
            return names, numbers

        visitor_team = reverse_team_map[str(soup.find('table', attrs={'id': 'Visitor'}).find_all('img')[0].attrs['alt'])]
        home_team = reverse_team_map[str(soup.find('table', attrs={'id': 'Home'}).find_all('img')[1].attrs['alt'])]

        kept_rows = []
        for row in rows:
            players_on_ice = ['', '']
            table = row.find('table')
            if table is not None:
                names, nums = parse_players_on_ice_table(table)
                players_on_ice[0] = ' | '.join(['{0} - {1}'.format(name, num) for name, num in zip(names, nums)])
                table.extract()
            table = row.find('table')
            if table is not None:
                names, nums = parse_players_on_ice_table(table)
                players_on_ice[1] = ' | '.join(['{0} - {1}'.format(name, num) for name, num in zip(names, nums)])
                table.extract()
            values = [c.text.replace('\xa0', '').replace('\n', ' ') for c in row.find_all('td')][:-2]
            values += players_on_ice
            kept_rows.append(dict(zip(cols, values)))

        return pd.DataFrame(kept_rows).set_index('#'), home_team, visitor_team
