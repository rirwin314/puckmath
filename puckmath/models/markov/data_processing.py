import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import urllib
import string
import os
import multiprocessing
import pickle
import json

from bs4 import BeautifulSoup
from tqdm import tqdm_notebook as tqdm
from datetime import datetime
from puckmath.interfaces.nhl import HtmlReports, reverse_team_map


def time_str_to_seconds(s):
    vals = s.split(':')
    assert len(vals) == 2
    return int(vals[0]) * 60 + int(vals[1])


def parse_play_by_play_dataframe(df, ht, vt):
    def rename_event(event_str, desc_str, home_team, visitor_team, prev_event_str):
        tdict = {home_team: 'HOME ', visitor_team: 'VISITOR '}
        if event_str == 'FAC':
            zone = desc_str.split('won ')[1].split(' -')[0]
            tm = desc_str.split(' ')[0]
            event_str = tdict.get(tm, tm) + 'FAC ' + zone
        elif event_str == 'PENL':
            tm = desc_str.split(' ')[0]
            event_str = tdict.get(tm, tm) + 'PENL'
        elif event_str == 'STOP':
            event_str = desc_str
            if 'GOALIE' in event_str:
                if 'GOALIE' not in prev_event_str:
                    if 'VISITOR' in prev_event_str:
                        event_str = 'HOME ' + event_str.split(',')[0]
                    elif 'HOME' in prev_event_str:
                        event_str = 'VISITOR ' + event_str.split(',')[0]
                else:
                    event_str = prev_event_str
        elif event_str == 'HIT':
            tm = desc_str.split(' ')[0]
            event_str = tdict.get(tm, tm) + 'HIT'
        elif event_str in ('MISS', 'SHOT', 'GOAL'):
            tm = desc_str.split(' ')[0]
            st = desc_str.split(',')[1].strip()
            zn = desc_str.split(',')[3].strip() if event_str == 'MISS' else desc_str.split(',')[2].strip()
            event_str = '{}{}'.format(tdict[tm], event_str)
        elif event_str in ('GIVE', 'TAKE'):
            tm = desc_str[:3]
            event_str = tdict.get(tm, tm) + event_str
        elif event_str == 'BLOCK':
            tm = desc_str.split(' ')[0]
            event_str = tdict.get(tm, tm) + 'BLOCK'
        prev_event_str = event_str
        return event_str

    df['Elapsed (s)'] = [time_str_to_seconds(s.split()[0]) for s in list(df['Time: Elapsed Game'])]
    df['Time Delta'] = [np.nan] + list(np.array(df['Elapsed (s)'][1:]) - np.array(df['Elapsed (s)'][:-1]))
    df['Time Delta'] = [t if t > 0 else 0 for t in df['Time Delta']]

    filtered_events = ['PGSTR', 'PGEND', 'ANTHEM', 'PSTR', 'PEND', 'GEND', 'GOFF']
    filt = lambda x: x not in filtered_events
    df = df[(df['Event'].map(filt))]

    new_df = pd.DataFrame(columns=['source_event', 'dest_event', 'time_delta'])
    prev_event_str = ''
    source_events = []
    dest_events = []
    for se, sd, de, dd in zip(list(df['Event'])[:-1], list(df['Description'])[:-1], list(df['Event'])[1:],
                              list(df['Description'])[1:]):
        src = rename_event(se, sd, ht, vt, prev_event_str)
        prev_event_str = src
        dest = rename_event(de, dd, ht, vt, prev_event_str)
        prev_event_str = dest
        source_events.append(src)
        dest_events.append(dest)
    new_df['source_event'] = source_events
    new_df['dest_event'] = dest_events
    new_df['time_delta'] = list(df['Time Delta'])[1:]
    return new_df


def process_one_game(game, year, version):
    df_dict = {}
    try:
        if game % 100 == 0:
            print('Working on game ', game)

        dest_fnm = 'parsed_dataframes/{}_{}_{}_{}_{}.csv'.format('PL', year, 'regular', game, version)
        dest_metadata = 'parsed_dataframes/{}_{}_{}_{}_{}_meta.json'.format('PL', year, 'regular', game, version)
        if os.path.exists(dest_fnm) and os.path.exists(dest_metadata):
            parsed_df = pd.read_csv(dest_fnm)
            with open(dest_metadata, 'r') as f:
                meta_data = json.load(f)
            ht = meta_data['home_team']
            vt = meta_data['visitor_team']
        else:
            df, ht, vt = HtmlReports.read_report('PL', year, 'regular', game)
            parsed_df = parse_play_by_play_dataframe(df, ht, vt)
            parsed_df.to_csv(dest_fnm)
            with open(dest_metadata, 'w') as f:
                json.dump({'home_team': ht, 'visitor_team': vt}, f)

        if (ht, vt) in df_dict:
            df_dict[(ht, vt)].append(parsed_df)
        else:
            df_dict[(ht, vt)] = [parsed_df]
    except Exception as e:
        print(e)
        print('Error cannot process game {}'.format(game))
    return df_dict


def get_master_df_dict(year, start_game, end_game, version=3):
    master_df_dict = {}
    ngames = end_game - start_game + 1

    dest_fnm = 'parsed_dataframes/master_df_dict_{:04d}_{:04d}_{:04d}_v{:02d}.bin'.format(year, start_game, end_game,
                                                                                          version)

    if os.path.exists(dest_fnm):
        with open(dest_fnm, 'rb') as f:
            master_df_dict = pickle.load(f)
    else:
        print('Beginning multiprocessing')
        pool = multiprocessing.Pool(processes=4)
        results = pool.starmap(process_one_game, zip(
            np.arange(start_game, end_game + 1),
            np.zeros(ngames, dtype=int) + year,
            np.zeros(ngames, dtype=int) + version))
        print('Completed multiprocessing')

        master_df_dict = {}
        for result in results:
            for k in result:
                if k in master_df_dict:
                    master_df_dict[k].extend(result[k])
                else:
                    master_df_dict[k] = result[k]
        with open(dest_fnm, 'wb') as f:
            pickle.dump(master_df_dict, f)

    return master_df_dict