from string import ascii_lowercase
import os
import requests

from puckmath.config.file import ConfigFile


def download_players():
    data_directory = ConfigFile.get_key('local', 'data_directory')

    for c in ascii_lowercase:
        print('Reading player names "{0}"'.format(c.upper()))

        player_id_fnm = os.path.join(data_directory, 'hockey_ref', 'hr_players_{0}.html'.format(c))

        link = 'http://www.hockey-reference.com/players/{0}'.format(c)
        print('Reading HTML from link: {0}'.format(link))
        req = requests.get(link, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            # 'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        })
        html = req.text

        os.makedirs(os.path.split(player_id_fnm)[0], exist_ok=True)
        with open(player_id_fnm, 'wb') as f:
            f.write(html.encode("utf-8"))
