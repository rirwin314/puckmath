import json
import os
import logging

from datetime import datetime, timedelta

import requests

base_url = 'https://statsapi.web.nhl.com/api/v1/'


def _to_game_time(event):
    period = event['about']['period']
    period_time = sum([int(ii) * jj for ii, jj in zip(event['about']['periodTime'].split(':'), [60, 1])])
    return (period - 1) * 20 * 60 + period_time


def fetch_game_data(year, game_type, game_number, data_dir='/scratch', cache=True, autoupdate=True):
    dest_path = os.path.join(data_dir, f'{year}', f'{game_type:02d}', f'{game_number:04d}', 'game_feed_live.json')

    if cache and os.path.exists(dest_path):
        with open(dest_path, 'r') as f:
            data = json.load(f)
        game_dt = datetime.strptime(data['metaData']['timeStamp'], '%Y%m%d_%H%M%S')
        if not autoupdate or datetime.utcnow() - game_dt > timedelta(weeks=2):
            return data

    url = base_url + f'game/{year}{game_type:02d}{game_number:04d}/feed/live'
    resp = requests.get(url)
    data = resp.json()

    if 'messageNumber' in data:
        logging.error(f'Data did not download correctly')
        logging.error(f'{json.dumps(data, indent=2)}')
        return data

    if cache:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w') as f:
            json.dump(data, f, indent=2)

    return data


def annotate_strength(game_data):
    team_data = game_data['gameData']['teams']
    all_plays = game_data['liveData']['plays']['allPlays']

    penalties = [play for play in all_plays if play['result']['eventTypeId'] == 'PENALTY']
    goals = {
        team: [play for play in all_plays if play['result']['eventTypeId'] == 'GOAL'
               and play['team']['id'] == team_data[team]['id']]
        for team in ['home', 'away']
    }
    penalty_ranges = {
        team: [[_to_game_time(penalty), _to_game_time(penalty) + 60 * penalty['result']['penaltyMinutes']]
               for penalty in penalties if penalty['team']['id'] == team_data[team]['id']
               and penalty['result']['penaltyMinutes'] != 10]
        for team in ['home', 'away']
    }

    # NHL penalty logic
    remove_coincidental_penalty_ranges = {
        t1: [rng for rng in penalty_ranges[t1] if rng not in penalty_ranges[t2]]
        for t1, t2 in zip(['home', 'away'], ['away', 'home'])
    }
    truncate_penalty_ranges = remove_coincidental_penalty_ranges.copy()
    for t1, t2 in zip(['home', 'away'], ['away', 'home']):
        for goal in goals[t1]:
            for rng in truncate_penalty_ranges[t2]:
                if rng[0] < _to_game_time(goal) < rng[1]:
                    rng[1] = _to_game_time(goal)
                    break

    for play in all_plays:
        event_time = _to_game_time(play)
        in_box = {
            t: sum([1 for rng in truncate_penalty_ranges[t] if rng[0] < event_time < rng[1]]) for t in ['home', 'away']
        }
        play['onIce'] = {t: 5 - min(in_box[t], 2) for t in ['home', 'away']}
    return game_data