import urllib
import os
import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from puckmath.interfaces.utils import download_html

DATA_DIRECTORY = os.environ.get('PUCKMATH_DATA_DIRECTORY', '/tmp/data')


def logger():
    return logging.getLogger('hockeyref')


class HockeyRef(object):
    last_downloaded = None
    desired_delay = 10  # in seconds

    def __init__(self):
        raise RuntimeError('HockeyRef should not be instantiated')

    @staticmethod
    def _download_html(url, file_path):
        """
        Wrapper to prevent downloading too frequently
        :param url:
        :param file_path:
        :return:
        """
        if os.path.exists(file_path):
            return url

        if HockeyRef.last_downloaded is None:
            time_diff = HockeyRef.desired_delay + 1
        else:
            time_diff = (datetime.now() - HockeyRef.last_downloaded).seconds
        if time_diff < HockeyRef.desired_delay:
            logger().info('Waiting for HockeyRef HTML request ({0} seconds)')
            time.sleep(HockeyRef.desired_delay - time_diff)

        HockeyRef.last_downloaded = datetime.now()
        return download_html(url, file_path)

    @staticmethod
    def player_info_from_name(name):
        data = {
            'hint': '',
            'search': name,
            'pid': '',
            'idx': ''
        }
        url = 'https://www.hockey-reference.com/search/search.fcgi?{}'.format(urllib.parse.urlencode(data))
        file_path = os.path.join(DATA_DIRECTORY, 'hockeyref', 'search', '{0}_{1}.html'.format(name, datetime.now().strftime('%y')))
        redirect_url = HockeyRef._download_html(url, file_path)

        metadata = {
            'name': None,
            'years': [None, None],
            'league': None,
            'team': None,
            'id': None
        }

        if redirect_url.startswith('https://www.hockey-reference.com/players/'):
            metadata['id'] = redirect_url.split('https://www.hockey-reference.com/players/')[1].split('.html')[0]
            import shutil
            new_file_path = os.path.join(DATA_DIRECTORY, 'hockeyref', 'player', '{0}_{1}.html'.format(
                metadata['id'], datetime.now().strftime('%y%m%d')))
            shutil.copyfile(file_path, new_file_path)

            info_dict, dataframes = HockeyRef.load_player(metadata['id'])
            metadata['name'] = info_dict['name']
            metadata['league'] = 'NHL'
            metadata['team'] = info_dict['team']
            metadata['years'] = [None, None]
        else:
            try:
                with open(file_path, 'rb') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # only need the top search result
                search_item = soup.find(class_='search-item')

                info = search_item.find(class_='search-item-name').find('a').text
                url = search_item.find(class_='search-item-url')
                metadata['id'] = '/'.join(url.text.split('/')[-2:]).split('.')[0]

                metadata['name'] = ' '.join(info.split(' ')[:-1])
                metadata['years'] = [int(s) for s in info.split('(')[-1][:-1].split('-')]

                metadata['league'] = search_item.find(class_='search-item-league').text
                metadata['team'] = search_item.find(class_='search-item-team').text.split('Last Played for the ')[-1]
            except Exception as e:
                logger().error('Cannot parse file -- deleting downloaded html')
                os.remove(file_path)
                raise e

        return metadata

    @staticmethod
    def id_from_name(name):
        return HockeyRef.player_info_from_name(name)['id']

    @staticmethod
    def _load_html_soup(url, file_path):
        HockeyRef._download_html(url, file_path)
        with open(file_path, 'r') as f:
            string_data = f.read()

        soup = BeautifulSoup(string_data.replace('<!--\n', '').replace('\n-->', ''), 'html.parser')
        return soup

    @staticmethod
    def _load_info(soup):
        """
        Will need a safe way to handle each of these line attempts
        :param soup:
        :return:
        """
        info_data = {}
        info_soup = soup.find(id='info')
        try:
            info_data['photo_url'] = info_soup.find(class_='media-item').find('img').attrs['src']
        except Exception as e:
            logger().warning(e)
            info_data['photo_url'] = None

        try:
            info_data['name'] = info_soup.find(itemprop='name').text
        except Exception as e:
            logger().warning(e)
            info_data['name'] = None

        try:
            info_data['height'] = tuple([int(ii.split(',')[0]) for ii in
                                         info_soup.find(itemprop='height').text.split('-')])
        except Exception as e:
            logger().warning(e)
            info_data['height'] = [None, None]

        try:
            info_data['weight'] = int(info_soup.find(itemprop='weight').text.split('lb')[0])
        except Exception as e:
            logger().warning(e)
            info_data['weight'] = None

        try:
            info_data['team'] = info_soup.find(itemprop='affiliation').text
        except Exception as e:
            logger().warning(e)
            info_data['team'] = None

        try:
            info_data['born_date'] = datetime.strptime(info_soup.find(id='necro-birth').attrs['data-birth'], '%Y-%m-%d')
        except Exception as e:
            logger().warning(e)
            info_data['born_date'] = None

        try:
            info_data['born_city'] = ' '.join(info_soup.find(itemprop='birthPlace').text.replace(
                '\xa0', ' ').split()[1:])
        except Exception as e:
            logger().warning(e)
            info_data['born_city'] = None

        # Onto soup text
        soup_text = info_soup.text.replace('\xa0', ' ')

        try:
            info_data['position'] = soup_text.split('Position: ')[1].split()[0]
        except Exception as e:
            logger().warning(e)
            info_data['position'] = None
        try:
            if 'G' not in info_data['position']:
                info_data['handedness'] = soup_text.split('Shoots: ')[1].split()[0]
        except Exception as e:
            logger().warning(e)
            info_data['handedness'] = None

        try:
            info_data['drafted'] = soup_text.split('Draft: ')[1].split('\n')[0]
        except Exception as e:
            logger().warning(e)
            info_data['drafted'] = None

        try:
            info_data['current_salary'] = soup_text.split('Current salary: ')[1].split()[0]
        except Exception as e:
            logger().warning(e)
            info_data['current_salary'] = None

        try:
            info_data['cap_hit'] = soup_text.split('cap hit: ')[1].split()[0]
        except Exception as e:
            logger().warning(e)
            info_data['cap_hit'] = None

        try:
            info_data['pronunciation'] = soup_text.split('Pronunciation: ')[1].split('\n')[0]
        except Exception as e:
            logger().warning(e)
            info_data['pronunciation'] = None

        return info_data

    @staticmethod
    def _convert_toi_to_s(val):
        try:
            vals = [float(v) for v in val.split(':')]
            if len(vals) == 2:
                return vals[0] * 60 + vals[1]
            elif len(vals) == 3:
                return vals[0] * 3600 + vals[1] * 60 + vals[2]
        except:
            return val

    @staticmethod
    def _parse_all_tables(soup):
        dataframes = {t.attrs['id']: pd.read_html(str(t), header=1, converters={'TOI': HockeyRef._convert_toi_to_s})[0]
                      for t in soup.find_all('table')}
        for key in dataframes:
            for col in dataframes[key].columns.values:
                try:
                    dataframes[key] = dataframes[key][dataframes[key][col] != col]
                    dataframes[key][col] = float(dataframes[key][col])
                except TypeError as e:
                    logger().warning('TypeError on (key, col): ({}, {})'.format(key, col))
                    logger().warning(e)
                    continue
                except ValueError as e:
                    logger().warning('ValueError on (key, col): ({}, {})'.format(key, col))
                    logger().warning(e)
                    continue
        return dataframes

    @staticmethod
    def load_player(id):
        url = 'https://www.hockey-reference.com/players/{0}.html'.format(id)
        file_path = os.path.join(DATA_DIRECTORY, 'hockeyref', 'players', '{0}_{1}.html'.format(
            id, datetime.now().strftime('%y%m%d')))

        soup = HockeyRef._load_html_soup(url, file_path)
        info_data = HockeyRef._load_info(soup)
        dataframes = HockeyRef._parse_all_tables(soup)

        return info_data, dataframes

    @staticmethod
    def load_player_advanced(id, strength):
        url = 'https://www.hockey-reference.com/players/{0}-advanced-{1}.html'.format(id, strength.lower())
        file_path = os.path.join(DATA_DIRECTORY, 'hockeyref', 'players', '{0}_{1}.html'.format(
            id, datetime.now().strftime('%y%m%d')))

        soup = HockeyRef._load_html_soup(url, file_path)
        info_data = HockeyRef._load_info(soup)
        dataframes = HockeyRef._parse_all_tables(soup)

        return info_data, dataframes

    @staticmethod
    def load_game_logs(id, year):
        url = 'https://www.hockey-reference.com/players/{0}/gamelog/{1}'.format(id, year)
        file_path = os.path.join(DATA_DIRECTORY, 'hockeyref', 'gamelog', '{0}_{1}.html'.format(
            id, datetime.now().strftime('%y%m%d')))

        soup = HockeyRef._load_html_soup(url, file_path)
        info_data = HockeyRef._load_info(soup)
        dataframes = HockeyRef._parse_all_tables(soup)

        return info_data, dataframes

