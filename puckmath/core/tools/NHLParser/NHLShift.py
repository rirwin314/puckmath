from puckmath.core.tools.NHLParser.utils import _text_to_time


class NHLShift(object):
    def __init__(self, soup):
        self.soup = soup

        cols = soup.find_all('td')
        self.shift_num = int(cols[0].text)
        if 'OT' in cols[1].text:
            self.period_num = 4
        else:
            self.period_num = int(cols[1].text)
        _start_text = cols[2].text
        _elapsed_text = _start_text.split('/')[0].strip()
        _remain_text = _start_text.split('/')[1].strip()
        self.shift_start_elapsed = _text_to_time(_elapsed_text)
        self.shift_start_remaining = _text_to_time(_remain_text)
        _end_text = cols[3].text
        _elapsed_text = _end_text.split('/')[0].strip()
        _remain_text = _end_text.split('/')[1].strip()
        self.shift_end_elapsed = _text_to_time(_elapsed_text)
        self.shift_end_remaining = _text_to_time(_remain_text)
        self.duration = _text_to_time(cols[4].text)
        self.event_string = cols[5].text
