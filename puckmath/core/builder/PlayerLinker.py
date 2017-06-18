"""
The player linker links GamePlayerAssociations to unique Player objects.
"""
import logging
import os
from string import ascii_lowercase

import requests
from tqdm import tqdm

from puckmath.core.schema import *


def parse_player_info(session, data_path):
    """
    Downloads and parses player info from hockey-reference.com
    :param session:
    :param data_path:
    :return:
    """
    dat_to_add = []
    for c in ascii_lowercase:
        logging.debug('Reading player names "{0}"'.format(c.upper()))

        player_id_fnm = os.path.join(data_path, 'hr_players_{0}.html'.format(c))

        if not os.path.isfile(player_id_fnm):
            link = 'http://www.hockey-reference.com/players/{0}'.format(c)
            logging.debug('Reading HTML from link: {0}'.format(link))
            req = requests.get(link, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'
            })
            html = req.text

            with open(player_id_fnm, 'w') as f:
                f.write(html)
        else:
            with open(player_id_fnm, 'r') as f:
                html = f.read()

        pdat = html.split('<p class="nhl">')
        for pl in pdat[1:]:
            try:
                pl_id = pl.split('</p>')[0].split('/players/')[1].split('.html')[0]
            except Exception as e:
                logging.error('Could not get player id from: {0}'.format(pl))
                logging.error(e)
                continue

            try:
                name = pl.split('">')[1].split('<')[0]
            except Exception as e:
                logging.error('Could not get name from: {0}'.format(pl))
                logging.error(e)
                continue

            try:
                min_yr = int((pl.split('(')[1]).split('-')[0])
                max_yr = int((pl.split('(')[1]).split('-')[1].split(',')[0])
            except Exception as e:
                logging.error('Could not get year range from: {0}'.format(pl))
                logging.error(e)
                pos = pl.split('(')[1].split(')')[0]
                min_yr = 'NULL'
                max_yr = 'NULL'
            else:
                pos = pl.split('(')[1].split(',')[1].split(')')[0]

            dat_to_add.append({
                'unique_id': pl_id,
                'full_name': name,
                'start_year': min_yr,
                'last_year': max_yr,
                'position': pos.strip()
            })

    keys = ['unique_id', 'full_name', 'start_year', 'last_year', 'position']
    for dat in dat_to_add:
        p = Player.Player(player_id=dat['unique_id'], full_name=dat['full_name'].upper(), start_year=dat['start_year'],
                          last_year=dat['last_year'], position=dat['position'])
        session.merge(p)


def link_gpas_to_players_href(session):
    """
    Link the GPAs to Player instances piggybacking off of the hockey-reference.com search engine.
    :param session:
    :return:
    """

    gpas = session.query(GamePlayerAssociation.GamePlayerAssociation).filter(
        GamePlayerAssociation.GamePlayerAssociation.player == None).all()

    print('Need to link {0} player records!'.format(len(gpas)))

    unmatched_names = []
    nm_pid_map = {}
    for gpa in tqdm(gpas):
        if gpa.player_name in nm_pid_map:
            gpa.player_id = nm_pid_map[gpa.player_name]
        else:
            nm = gpa.player_name
            nm = nm.replace("'", '')
            nm = str([c for c in nm if c in ascii_lowercase or c == ' '])

            search_url = 'http://www.hockey-reference.com/search/search.fcgi?hint=&search={}&pid='.format(
                '+'.join([nm.split()[0], nm.split()[-1]]))

            resp = requests.get(search_url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'
            })

            pl_str = '/'.join(resp.url.split('/')[-2:]).split('.html')[0]

            if '?' not in pl_str and len(pl_str) <= 11:
                pl_obj = session.query(Player.Player).filter(Player.Player.player_id == pl_str).all()

                if not len(pl_obj):
                    session.add(Player.Player(player_id=pl_str, full_name=gpa.player_name))

                gpa.player_id = pl_str
                nm_pid_map[gpa.player_name] = pl_str
            else:
                if gpa.player_name not in unmatched_names:
                    unmatched_names.append(gpa.player_name)

    with open('players_to_link.txt', 'w') as f:
        f.writelines('\n'.join(unmatched_names))


def link_gpas_to_players(session):
    """
    Deprecated -- Link GPAs to Player instances using some logic. Using hockey-reference is the preferred method.
    :param session:
    :return:
    """
    from sqlalchemy import and_
    from string import ascii_uppercase

    def _match_filter(g):
        def similar_pos(p1, p2):
            if 'D' in p1 and 'D' in p2:
                return True
            if 'G' in p1 and 'G' in p2:
                return True
            if p1 in ('C', 'LW', 'RW') and p2 in ('C', 'LW', 'RW'):
                return True
            return False

        nm = g.player_name
        nm = nm.replace("'", '')
        nm = nm.replace("-", '')
        dat = session.query(Player.Player).filter(and_(
            Player.Player.full_name.like('%'.join([n[0] for n in
                                                   nm.split()[:-1]]) + '%' + ''.join(
                [c for c in nm.split()[-1] if c in ascii_uppercase])),
            Player.Player.start_year - 1 <= g.game.start_datetime.year,
            Player.Player.last_year >= g.game.start_datetime.year)).all()

        if len(dat) == 0:
            nm = nm.lower()
            lastnm = ''.join(nm.split()[1:])
            plid = '{}/{}{}%'.format(lastnm[0], lastnm[:min(5, len(lastnm))], nm.split()[0][:2])
            dat = session.query(Player.Player).filter(and_(
                Player.Player.player_id.like(plid),
                Player.Player.start_year - 1 <= g.game.start_datetime.year,
                Player.Player.last_year >= g.game.start_datetime.year)).all()

        if len(dat) == 1:
            return dat[0]
        elif len(dat) > 1:
            m = None
            for pl in dat:
                if pl.full_name == g.player_name:
                    if m is None:
                        m = pl
                    else:
                        m = None
                        break

            if m is not None:
                return m

            m = None
            for pl in dat:
                if similar_pos(pl.position, g.position):
                    if m is None:
                        m = pl
                    else:
                        m = None
                        break

            if m is not None:
                return m

        return None

    gpas = session.query(GamePlayerAssociation.GamePlayerAssociation).filter(
        GamePlayerAssociation.GamePlayerAssociation.player == None).all()

    print('Need to link {0} player records!'.format(len(gpas)))

    unmatched_pls = []
    for gpa in tqdm(gpas):
        pl = _match_filter(gpa)
        if pl:
            gpa.player = _match_filter(gpa)
        else:
            if gpa.player_name not in unmatched_pls:
                unmatched_pls.append(gpa.player_name)

    with open('players_to_link.txt', 'w') as f:
        f.writelines('\n'.join(unmatched_pls))


def patch_game_times(session):
    """
    Small patch to deal with invalid game starting times.
    :param session: puckmath session
    :return: None
    """
    from datetime import datetime
    gs = session.query(Game.Game).filter(Game.Game.start_datetime == None).all()

    for g in tqdm(gs):
        yr = int(g.game_id[0:4])
        g.start_datetime = datetime(year=yr, month=1, day=1)
        session.merge(g)
