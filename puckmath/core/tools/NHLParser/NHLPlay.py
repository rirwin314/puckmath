class NHLPlay(object):
    def __init__(self):
        self.sequence = None
        self.period = None
        self.strength = None
        self.time_elapsed = None
        self.time_remaining = None
        self.type = None
        self.description = None

        self.away_names = None
        self.away_jersey_numbers = None
        self.away_positions = None

        self.home_names = None
        self.home_jersey_numbers = None
        self.home_positions = None

    def parse_away_on_ice(self, soup):
        self.soup = soup

        info = soup.find_all('font')

        self.away_names = []
        self.away_jersey_numbers = []
        self.away_positions = []

        for inf in info:
            try:
                txt = inf.attrs['title']
            except KeyError:
                continue

            self.away_names.append(txt.split('-')[1].strip())
            self.away_positions.append(txt.split(' ')[0])
            self.away_jersey_numbers.append(int(inf.text))

        return len(info)

    def parse_home_on_ice(self, soup):
        info = soup.find_all('font')

        self.home_names = []
        self.home_jersey_numbers = []
        self.home_positions = []

        for inf in info:
            try:
                txt = inf.attrs['title']
            except KeyError:
                continue

            self.home_names.append(txt.split('-')[1].strip())
            self.home_positions.append(txt.split(' ')[0])
            self.home_jersey_numbers.append(int(inf.text))

        return len(info)

    def __repr__(self):
        return '{0} - {1}'.format(self.type, self.description)