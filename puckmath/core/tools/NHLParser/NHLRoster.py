from bs4 import BeautifulSoup
from puckmath.core.tools.NHLParser.utils import html_rep, beautiful_soup_load
from puckmath.core.tools.NHLParser.NHLGameInfo import NHLGameInfo


class NHLRoster(object):
    def __init__(self):
        self.game_info = None

        self.away_jersey_numbers = None
        self.away_positions = None
        self.away_names = None
        self.away_captain_status = None

        self.home_jersey_numbers = None
        self.home_positions = None
        self.home_names = None
        self.home_captain_status = None

        self.away_scratch_jersey_numbers = None
        self.away_scratch_positions = None
        self.away_scratch_names = None
        self.away_scratch_types = None
        self.away_scratch_captain_status = None

        self.home_scratch_jersey_numbers = None
        self.home_scratch_positions = None
        self.home_scratch_names = None
        self.home_scratch_types = None
        self.home_scratch_captain_status = None

        self.referee_numbers = None
        self.referee_names = None

        self.linesmen_numbers = None
        self.linesmen_names = None

        self.away_coach = None
        self.home_coach = None

        self.html_src = None

    def load(self, season, game_type, game_num, src_dir='.'):
        self.html_src = html_rep(season, game_type, game_num, 'RO', src_dir)

        if self.html_src is None:
            raise FileNotFoundError

        bs = beautiful_soup_load(self.html_src)
        self.soup = bs

        self.game_info = NHLGameInfo(bs)

        info_table = bs.find_all('table')[9]
        self.away_coach = info_table.find_all('table')[-7].find('td').text
        self.home_coach = info_table.find_all('table')[-6].find('td').text

        rosters = info_table.find_all('tr')[0]

        away_roster_table = rosters.find_all('table')[0]
        self.parse_away_roster(away_roster_table)

        home_roster_table = rosters.find_all('table')[1]
        self.parse_home_roster(home_roster_table)

        away_scratches_table = info_table.find_all('table')[-9]
        self.parse_away_scratches(away_scratches_table)

        home_scratches_table = info_table.find_all('table')[-8]
        self.parse_home_scratches(home_scratches_table)

        referees_table = info_table.find_all('table')[-4]
        self.parse_referees(referees_table)

        linesmen_table = info_table.find_all('table')[-3]
        self.parse_linesmen(linesmen_table)

    def parse_away_roster(self, away_roster_table):
        rows = away_roster_table.find_all('td')

        self.away_jersey_numbers = []
        self.away_positions = []
        self.away_names = []
        self.away_captain_status = []

        for itr in range(3, len(rows), 3):
            self.away_jersey_numbers.append(int(rows[itr].text))
            self.away_positions.append(rows[itr + 1].text)
            if '(' in rows[itr + 2].text.split()[-1]:
                self.away_captain_status.append(rows[itr + 2].text.split()[-1][1])
                self.away_names.append(' '.join(rows[itr + 2].text.split()[:-1]).strip())
            else:
                self.away_captain_status.append('')
                self.away_names.append(rows[itr + 2].text)

    def parse_home_roster(self, home_roster_table):
        rows = home_roster_table.find_all('td')

        self.home_jersey_numbers = []
        self.home_positions = []
        self.home_names = []
        self.home_captain_status = []

        for itr in range(3, len(rows), 3):
            self.home_jersey_numbers.append(int(rows[itr].text))
            self.home_positions.append(rows[itr + 1].text)
            if '(' in rows[itr + 2].text.split()[-1]:
                self.home_captain_status.append(rows[itr + 2].text.split()[-1][1])
                self.home_names.append(' '.join(rows[itr + 2].text.split()[:-1]).strip())
            else:
                self.home_captain_status.append('')
                self.home_names.append(rows[itr + 2].text)

    def parse_away_scratches(self, away_scratches_table):
        rows = away_scratches_table.find_all('td')[3:]

        self.away_scratch_jersey_numbers = []
        self.away_scratch_positions = []
        self.away_scratch_names = []
        self.away_scratch_types = []
        self.away_scratch_captain_status = []

        for itr in range(0, len(rows), 3):
            self.away_scratch_jersey_numbers.append(int(rows[itr].text))
            self.away_scratch_positions.append(rows[itr + 1].text)
            self.away_scratch_types.append('INJURED' if rows[itr + 2]['class'] == 'italic' else 'HEALTHY')
            if '(' in rows[itr + 2].text.split()[-1]:
                self.away_scratch_captain_status.append(rows[itr + 2].text.split()[-1][1])
                self.away_scratch_names.append(' '.join(rows[itr + 2].text.split()[:-1]).strip())
            else:
                self.away_scratch_captain_status.append('')
                self.away_scratch_names.append(rows[itr + 2].text)

    def parse_home_scratches(self, home_scratches_table):
        rows = home_scratches_table.find_all('td')[3:]

        self.home_scratch_jersey_numbers = []
        self.home_scratch_positions = []
        self.home_scratch_names = []
        self.home_scratch_types = []
        self.home_scratch_captain_status = []

        for itr in range(0, len(rows), 3):
            self.home_scratch_jersey_numbers.append(int(rows[itr].text))
            self.home_scratch_positions.append(rows[itr + 1].text)
            self.home_scratch_types.append('INJURED' if rows[itr + 2]['class'] == 'italic' else 'HEALTHY')
            if '(' in rows[itr + 2].text.split()[-1]:
                self.home_scratch_captain_status.append(rows[itr + 2].text.split()[-1][1])
                self.home_scratch_names.append(' '.join(rows[itr + 2].text.split()[:-1]).strip())
            else:
                self.home_scratch_captain_status.append('')
                self.home_scratch_names.append(rows[itr + 2].text)

    def parse_referees(self, referees_table):
        self.referee_numbers = []
        self.referee_names = []

        for td in referees_table.find_all('td'):
            self.referee_numbers.append(int(td.text.split(' ')[0][1:]))
            self.referee_names.append(' '.join(td.text.split(' ')[1:]))

    def parse_linesmen(self, linesmen_table):
        self.linesmen_numbers = []
        self.linesmen_names = []

        for td in linesmen_table.find_all('td'):
            self.linesmen_numbers.append(int(td.text.split(' ')[0][1:]))
            self.linesmen_names.append(' '.join(td.text.split(' ')[1:]))