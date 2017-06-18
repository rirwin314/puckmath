from puckmath.puckdb.nhl_parser.utils import text_to_time


class NHLTOIPeriodSummary(object):
    def __init__(self, soup, per):
        self.soup = soup
        cols = soup.find_all('td')
        self.period_num = per
        self.num_shifts = int(cols[1].text)
        self.average_shift_length = text_to_time(cols[2].text)
        self.toi = text_to_time(cols[3].text)
        self.ev_toi = text_to_time(cols[4].text)
        self.pp_toi = text_to_time(cols[5].text)
        self.sh_toi = text_to_time(cols[6].text)
