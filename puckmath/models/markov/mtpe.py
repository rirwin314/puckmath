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
from puckmath.models.data_processing import parse_play_by_play_dataframe, process_one_game, get_master_df_dict


def generate_markov_matrix_for_game(df_dict, home_team, away_team):
    """
    Build up the Markov transition matrix + Poisson extension (MT+PE) for a single game.
    """
    markov_matrix = {}

    def add_to_markov_matrix(source_event, dest_event, time_delta):
        if source_event not in markov_matrix:
            markov_matrix[source_event] = {}
        if dest_event not in markov_matrix[source_event]:
            markov_matrix[source_event][dest_event] = [0, []]
        markov_matrix[source_event][dest_event][0] += 1  # increment
        markov_matrix[source_event][dest_event][1].append(time_delta)

    for k in df_dict:
        if home_team == k[0] or away_team == k[1]:
            for parsed_df in df_dict[k]:
                for ii in range(len(parsed_df)):
                    add_to_markov_matrix(parsed_df.iloc[ii]['source_event'],
                                         parsed_df.iloc[ii]['dest_event'],
                                         parsed_df.iloc[ii]['time_delta'])
    return markov_matrix


def get_score(df):
    """
    Parse the event dataframe for the final score; this should be deprecated when a more global
    "generate game summary" function is completed.
    """
    home_score = 0
    visitor_score = 0
    for ii in range(len(df)):
        if ' GOAL ' in df.iloc[ii]['event']:
            if 'HOME' in df.iloc[ii]['event']:
                home_score += 1
            elif 'VISITOR' in df.iloc[ii]['event']:
                visitor_score += 1
    return home_score, visitor_score


def is_ot_game(df):
    return len(df[df['event'] == 'PEND']) == 4


def gen_sim(mat):
    """
    Generate a single game, regular season simulation for a given Markov transition + Poisson extension (MT+PE) matrix
    """
    default_event = lambda: 'HOME FAC Neu. Zone' if np.random.randint(2) == 1 else 'VISITOR FAC Neu. Zone'

    def get_next(current_event):
        """
        Generate the next event given the current event.
        """
        if current_event == 'HOME FAC Neu. Zone' and current_event not in mat:
            current_event = 'VISITOR FAC Neu. Zone'
        elif current_event == 'VISITOR FAC Neu. Zone' and current_event not in mat:
            current_event = 'HOME FAC Neu. Zone'
        next_event_possibilities = mat[current_event]
        keys = [k for k in next_event_possibilities]
        counts = [next_event_possibilities[k][0] for k in keys]
        weights = np.array(counts) / np.sum(counts)
        lambdas = {k: np.nanmean(next_event_possibilities[k][1]) for k in keys}
        choice = np.random.choice(keys, p=weights)
        elapsed_time = np.random.poisson(lam=lambdas[choice])
        # Error handling here -- something is amok with the MT+PE matrix
        if choice in mat:
            return choice, elapsed_time
        else:
            return default_event(), 0

    # Begin with an empty event dataframe.
    event_df = pd.DataFrame(columns=['event', 'time_elapsed'])
    # Tracking variables
    period = 1
    time_elapsed = 0
    game_over = False
    # Assume home team wins the opening draw for now
    event_df = event_df.append([{'event': default_event(), 'time_elapsed': 0}], ignore_index=True)

    while not game_over:
        next_event, delta_t = get_next(event_df.iloc[-1]['event'])
        if period < 4:
            if time_elapsed + delta_t > 1200:
                event_df = event_df.append({'event': 'PEND', 'time_elapsed': 1200}, ignore_index=True)
                time_elapsed = 0
                if period == 3 and get_score(event_df)[0] != get_score(event_df)[1]:
                    game_over = True
                else:
                    # Start the next period
                    event_df = event_df.append([{'event': default_event(), 'time_elapsed': 0}], ignore_index=True)
                    period += 1
            else:
                event_df = event_df.append({'event': next_event, 'time_elapsed': time_elapsed + delta_t},
                                           ignore_index=True)
                time_elapsed += delta_t
        elif period == 4:
            if time_elapsed + delta_t > 300:
                game_over = True  # TODO: handle shootout
                event_df = event_df.append({'event': 'PEND', 'time_elapsed': np.nan}, ignore_index=True)
            else:
                event_df = event_df.append({'event': next_event, 'time_elapsed': time_elapsed + delta_t},
                                           ignore_index=True)
                time_elapsed += delta_t
                if ' GOAL ' in next_event:
                    game_over = True
                    event_df = event_df.append({'event': 'PEND', 'time_elapsed': np.nan}, ignore_index=True)

    event_df = event_df.append({'event': 'GEND', 'time_elapsed': np.nan}, ignore_index=True)
    return event_df, get_score(event_df)


def gen_monte_carlo(mat, num_iters=100):
    results = []
    for ii in range(num_iters):
        results.append(gen_sim(mat))
    return results


def sim_for_schedule(schedule, master_df_dict, iters):
    sim_results = pd.DataFrame(
        columns=['date', 'home_team', 'visitor_team', 'home_goals', 'visitor_goals', 'status', 'sim_home_goals',
                 'sim_visitor_goals', 'sim_status'])
    sim_dataframes = []

    for visitor, home, date, status, visitor_goals, home_goals in zip(schedule['Visitor'], schedule['Home'],
                                                                      schedule['Date'], schedule['Unnamed: 5'],
                                                                      schedule['G'], tqdm(schedule['G.1'])):
        row_data = {}
        row_data['visitor_team'] = reverse_team_map[visitor.upper()]
        row_data['home_team'] = reverse_team_map[home.upper()]
        row_data['date'] = date
        row_data['status'] = status
        row_data['home_goals'] = home_goals
        row_data['visitor_goals'] = visitor_goals

        markov_matrix = generate_markov_matrix_for_game(master_df_dict, row_data['home_team'], row_data['visitor_team'])
        results = gen_monte_carlo(markov_matrix, num_iters=iters)

        sim_dataframes.append([r[0] for r in results])

        score = [0, 0]
        if iters == 1:
            score[0] = results[0][1][0]
            score[1] = results[0][1][1]
            # if is_ot_game(df):
            #     row_data['sim_status'] = 'OT' if score[0] != score[1] else 'SO'
            # else:
            #     row_data['sim_status'] = None
        else:
            score[0] = np.sum([int(r[1][0] > r[1][1]) for r in results]) / iters
            score[1] = np.sum([int(r[1][0] < r[1][1]) for r in results]) / iters

        row_data['sim_home_goals'] = score[0]
        row_data['sim_visitor_goals'] = score[1]

        sim_results = sim_results.append(row_data, ignore_index=True)

    sim_results['correctness'] = ~((sim_results['home_goals'] > sim_results['visitor_goals']) ^ (
    sim_results['sim_home_goals'] > sim_results['sim_visitor_goals']))
    sim_results['correctness'] = sim_results['correctness'].map(int)

    return sim_results, sim_dataframes


def sim_for_date(date, master_df_dict, schedule, iters=10):
    scheduled_games = schedule[schedule['Date'] == date.strftime('%Y-%m-%d')]
    return sim_for_schedule(scheduled_games, master_df_dict, iters)