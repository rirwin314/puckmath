from bs4 import BeautifulSoup
from puckmath.core.tools.NHLParser.utils import html_rep, beautiful_soup_load
from puckmath.core.tools.NHLParser.NHLGameInfo import NHLGameInfo
from puckmath.core.tools.NHLParser.NHLPlay import NHLPlay
from datetime import time


class NHLPlayByPlay(object):
    def __init__(self):
        self.html_src = None
        self.game_info = None
        self.plays = None

    def load(self, season, game_type, game_num, src_dir='.'):
        self.html_src = html_rep(season, game_type, game_num, 'PL', src_dir)

        self.soup = beautiful_soup_load(self.html_src)

        self.game_info = NHLGameInfo(self.soup)
        self.parse_events()

    def parse_events(self):
        events = self.soup.find_all('tr', {'class': 'evenColor'})
        self.plays = []

        for event in events:
            entries = event.find_all('td')

            _safe_int = lambda x: int(x) if x.isnumeric() else None

            p = NHLPlay()
            try:
                p.sequence = _safe_int(entries[0].text)
                p.period = _safe_int(entries[1].text)
                p.strength = entries[2].text
                p.description = entries[5].text
            except ValueError:
                print(entries)
                raise ValueError

            try:
                p.time_elapsed = time(minute=int(entries[3].text.split(':')[0]),
                                      second=int(entries[3].text.split(':')[1][:2]))
                p.time_remaining = time(minute=int(entries[3].text.split(':')[1][2:]),
                                        second=int(entries[3].text.split(':')[2]))
            except ValueError as e:
                print('Cannot parse')
                print(p.description)
                continue

            p.type = entries[4].text
            try:
                cnt = p.parse_away_on_ice(entries[6])
                cnt = p.parse_home_on_ice(entries[6+4*cnt])
            except ValueError as e:
                print('Cannot parse')
                print(p.description)
                continue

            self.plays.append(p)