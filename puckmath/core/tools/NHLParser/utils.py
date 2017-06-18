import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
import os


def html_rep(season, game_type, game_num, rep_code, src_dir='.'):
    """Retrieves the nhl html reports for the specified game and report code"""
    __domain = 'http://www.nhl.com/'
    file_name = os.path.join(src_dir, 'htmlreports', '{0}{1}'.format(str(season-1), str(season)),
                             '{0}0{1}{2:04d}.HTM'.format(rep_code, str(game_type), game_num))

    url = [__domain, "scores/htmlreports/", str(season - 1), str(season),
           "/", rep_code, "0", str(game_type), ("%04i" % (game_num)), ".HTM"]
    url = ''.join(url)

    print('Working on: {0}'.format(url))
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='latin-1') as f:
            return f.read()

    req = None
    html_src = None
    try:
        req = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        })
        html_src = req.text
    except Exception as e:
        print(e)

    if '404 Not Found' in html_src:
        return None

    with open(file_name, 'w') as f:
        f.write(html_src)

    return html_src


def _text_to_time(txt):
    """
    Returns a datetime.time object from a string
    :param txt:
    :return:
    """
    splits = txt.split(':')

    hours = 0
    minutes = 0
    seconds = 0

    if len(splits) == 2:
        hours = 0
        minutes = int(splits[0])
        seconds = int(splits[1])

        if minutes >= 60:
            hours = int(minutes/60)
            minutes -= hours*60
    if len(splits) == 3:
        hours = int(splits[0])
        minutes = int(splits[1])
        seconds = int(splits[2])

    try:
        time_object = time(hour=hours, minute=minutes, second=seconds)
    except (TypeError, ValueError):
        time_object = time(0)

    return time_object


def beautiful_soup_load(html):
    from bs4 import BeautifulSoup

    replacers = {
        '&nbsp;': ' ',
        'T.B': 'TBL',
        'S.J': 'SJS',
        'N.J': 'NJD',
        'L.A': 'LAK',
        '(maj)': ''
    }

    for k,v in replacers.items():
        html = html.replace(k, v)

    return BeautifulSoup(' '.join(html.split()), 'lxml')
