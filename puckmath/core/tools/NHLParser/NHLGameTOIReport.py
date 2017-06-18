from bs4 import BeautifulSoup
from puckmath.core.tools.NHLParser.utils import html_rep, beautiful_soup_load
from puckmath.core.tools.NHLParser.NHLGameInfo import NHLGameInfo
from puckmath.core.tools.NHLParser.NHLShift import NHLShift
from puckmath.core.tools.NHLParser.NHLTOIGameSummary import NHLTOIGameSummary
from puckmath.core.tools.NHLParser.NHLTOIPeriodSummary import NHLTOIPeriodSummary


class NHLGameTOIReport(object):
    def __init__(self):
        self.html_src = None
        self.player_jersey_numbers = None
        self.player_names = None
        self.player_shifts = None
        self.player_period_summaries = None
        self.player_game_summaries = None
        self.game_info = None
        self.soup = None

    def load(self, season, game_type, game_num, team='H', src_dir='.'):
        self.html_src = html_rep(season, game_type, game_num, 'T{0}'.format(team.upper()), src_dir)
        self.soup = beautiful_soup_load(self.html_src)

        self.game_info = NHLGameInfo(self.soup)
        self.parse_toi()

    @staticmethod
    def _get_shift(soup):
        if not soup.has_attr('class'):
            return None, None

        shift = NHLShift(soup)
        return shift, soup.findNext('tr')

    def parse_toi(self):
        player_data = [d for d in self.soup.find_all('td', {'class': 'playerHeading'})]
        self.player_names = [' '.join(' '.join(d.text.split(' ')[1:]).split(',')[::-1]).strip() for d in player_data]
        self.player_jersey_numbers = [int(d.text.split(' ')[0]) if d.text.split(' ')[0].isnumeric() else -1
                                      for d in player_data]
        self.player_shifts = [[] for _ in self.player_names]
        self.player_period_summaries = [[] for _ in self.player_names]
        self.player_game_summaries = []

        for period_summary, shifts, player in zip(self.player_period_summaries, self.player_shifts, player_data):
            soup_itr = player.findNext('tr').findNext('tr')

            while 1:
                shift, soup_itr = NHLGameTOIReport._get_shift(soup_itr)
                if shift is None:
                    break
                shifts.append(shift)

            ps_rows = player.findNext('table').findChildren('tr')[1:]
            for itr, row in enumerate(ps_rows):
                if itr == len(ps_rows)-1:
                    self.player_game_summaries.append(NHLTOIGameSummary(row))
                elif len(row.find_all('td')) > 0:
                    period_summary.append(NHLTOIPeriodSummary(row, itr+1))
