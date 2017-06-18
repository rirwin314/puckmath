from puckmath.core.tools.NHLParser.utils import _text_to_time


class NHLTOIPeriodSummary(object):
    def __init__(self, soup, per):
        self.soup = soup
        cols = soup.find_all('td')
        self.period_num = per
        self.num_shifts = int(cols[1].text)
        self.average_shift_length = _text_to_time(cols[2].text)
        self.toi = _text_to_time(cols[3].text)
        self.ev_toi = _text_to_time(cols[4].text)
        self.pp_toi = _text_to_time(cols[5].text)
        self.sh_toi = _text_to_time(cols[6].text)
