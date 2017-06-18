import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import os


class NHLGameInfo(object):
    def __init__(self, soup):
        self.soup = soup

        self.visitor_team = None
        self.visitor_game = None
        self.visitor_game_count = None

        self.home_team = None
        self.home_game = None
        self.home_game_count = None

        self.start_datetime = None
        self.end_datetime = None

        self.attendance = None
        self.venue = None

        self.game_num = None
        self.game_state = None

        game_info_table = soup.find('table', {'id': 'GameInfo'}).find_all('td')
        visitor_table = soup.find('table', {'id': 'Visitor'})

        self.visitor_team = visitor_table.find_all('tr')[-1].find('td').contents[0]
        self.visitor_game = int(visitor_table.find_all('tr')[-1].find('td').contents[2].split(' ')[1])
        self.visitor_game_count = int(visitor_table.find_all('tr')[-1].find('td').contents[2].split(' ')[-1])

        home_table = soup.find('table', {'id': 'Home'})

        self.home_team = home_table.find_all('tr')[-1].find('td').contents[0]
        self.home_game = int(home_table.find_all('tr')[-1].find('td').contents[2].split(' ')[1])
        self.home_game_count = int(home_table.find_all('tr')[-1].find('td').contents[2].split(' ')[-1])

        try:
            _date_text = game_info_table[3].text
        except Exception as e:
            print(e)
            print('Cannot parse date text')

        try:
            _time_text = game_info_table[5].text
            _start_time = _time_text.split(':')[0][-2:] + ':' + _time_text.split(':')[1][:2]
        except Exception as e:
            print(e)
            print('Cannot parse time text')

        try:
            _attendance = game_info_table[4].text.replace('  ', ' ')
        except Exception as e:
            print(e)
            print('Cannot parse attendance')

        try:
            _game_num = game_info_table[6].text
        except Exception as e:
            print(e)
            print('Cannot parse game num')

        try:
            self.start_datetime = datetime.strptime(_date_text.strip(), '%A, %B %d, %Y') + timedelta(
                hours=12 + int(_start_time.split(':')[0][-2:].strip()), minutes=int(_start_time.split(':')[1][:2].strip()))
        except Exception as e:
            print(e)
            print('Cannot set datetime from date/time text [{0} || {1}]'.format(_time_text, _date_text))

        try:
            self.attendance = int(''.join(_attendance.split(' ')[1].strip().split(',')))
        except Exception as e:
            print(e)
            print('Cannot parse attendance {0}'.format(_attendance))

        try:
            self.venue = ' '.join(_attendance.split(' ')[3:])
        except Exception as e:
            print(e)
            print('Cannot parse venue {0}'.format(_attendance))

        try:
            self.game_num = int(_game_num.split(' ')[1])
            self.game_state = game_info_table[7].text
        except Exception as e:
            print(e)
            print('Cannot parse game num {0}'.format(_game_num))