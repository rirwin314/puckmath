import logging
from datetime import time

from puckmath.puckdb.builder.utils import *
from puckmath.puckdb.nhl_parser.roster import NHLRoster
from puckmath.puckdb.nhl_parser.play_by_play import NHLPlayByPlay
from puckmath.puckdb.nhl_parser.game_toi_report import NHLGameTOIReport
from puckmath.puckdb.schema.game import Game, GameLinesmanAssociation, GameOfficialAssociation
from puckmath.puckdb.schema.game_player_association import GamePlayerAssociation, PeriodTOISummary
from puckmath.puckdb.schema.scratch import Scratch
from puckmath.puckdb.schema.shift import Shift
from puckmath.puckdb.schema.official import Official
from puckmath.puckdb.schema.linesman import Linesman
from puckmath.puckdb.schema.play import PlayerOnIce, Play, PLAY_CONSTRUCTOR_MAP


class GameFactory(object):
    @property
    def logger(self):
        return logging.getLogger('GameFactory')

    def __init__(self):
        self.nhl_roster = None
        self.nhl_game_info = None
        self.nhl_plays = None
        self.nhl_home_toi_reports = None
        self.nhl_away_toi_reports = None

        self.game_id = None
        self.session = None
        self.season = None
        self.game_type = None
        self.game_num = None
        self.src_path = None

        self._game = None
        self._linesmen = None
        self._officials = None
        self._rosters = None
        self._scratches = None
        self._plays = None

    def _build_nhl_info(self):
        self.nhl_roster = NHLRoster()
        self.logger.info('Loading NHL roster')
        self.nhl_roster.load(self.season, self.game_type, self.game_num, self.src_path)

        self.logger.info('Reading Game Info')
        self.nhl_game_info = self.nhl_roster.game_info

        self.nhl_plays = NHLPlayByPlay()
        self.logger.info('Loading NHL Play-by-Play')
        self.nhl_plays.load(self.season, self.game_type, self.game_num, self.src_path)

        self.nhl_home_toi_reports = NHLGameTOIReport()
        self.logger.info('Loading NHL home TOI reports')
        self.nhl_home_toi_reports.load(self.season, self.game_type, self.game_num, 'H', self.src_path)

        self.nhl_away_toi_reports = NHLGameTOIReport()
        self.logger.info('Loading NHL away TOI reports')
        self.nhl_away_toi_reports.load(self.season, self.game_type, self.game_num, 'V', self.src_path)

    def _build_game_obj(self):
        try:
            duration = self.nhl_game_info.end_datetime - self.nhl_game_info.start_datetime

            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
        except TypeError:
            hours = 0
            minutes = 0
            seconds = 0

        self._game = Game(game_id=self.game_id, game_type=GAME_TYPE[self.game_type],
                          attendance=self.nhl_game_info.attendance, venue=self.nhl_game_info.venue,
                          home_team_id=self.home_team_id, away_team_id=self.away_team_id, home_goals=-1,
                          away_goals=-1, game_remarks='', overtimes='',
                          game_duration=time(hour=int(hours), minute=int(minutes), second=int(seconds)),
                          start_datetime=self.nhl_game_info.start_datetime,
                          end_datetime=self.nhl_game_info.end_datetime)

    def _build_linesmen(self):
        self._linesmen = []
        for linesman, jersey_num in zip(self.nhl_roster.linesmen_names, self.nhl_roster.linesmen_numbers):
            self.session.merge(Linesman(name=linesman.upper()))
            self._linesmen.append(GameLinesmanAssociation(
                linesman_id=linesman.upper(), game_id=self.game_id, linesman_jersey=jersey_num))
        self._game._linesmen = self._linesmen

    def _build_officials(self):
        self._officials = []
        for official, jersey_num in zip(self.nhl_roster.referee_names, self.nhl_roster.referee_numbers):
            self.session.merge(Official(name=official.upper()))
            self._officials.append(GameOfficialAssociation(
                official_id=official.upper(), game_id=self.game_id, official_jersey=jersey_num))
        self._game._officials = self._officials

    @staticmethod
    def build_game_id(season, game_type, game_num):
        return '{0}{1:02d}{2:04d}'.format(season, game_type, game_num)

    def _build_team_ids(self):
        self.home_team_id = team_to_abbr(self.nhl_game_info.home_team)
        self.away_team_id = team_to_abbr(self.nhl_game_info.visitor_team)

    @staticmethod
    def _build_roster(names, positions, jersey_numbers, captain_status, toi_reports, game_id, team_id):
        _roster = []
        for name, position, jersey_num, captain_status in zip(
                names, positions, jersey_numbers, captain_status):
            period_toi_summaries = []
            game_summary = None
            shifts = []

            for j, ps, gs, psh in zip(toi_reports.player_jersey_numbers, toi_reports.player_period_summaries,
                                      toi_reports.player_game_summaries, toi_reports.player_shifts):
                if j == jersey_num:
                    for p in ps:
                        period_toi_summaries.append(PeriodTOISummary(
                            period_num=p.period_num, num_shifts=p.num_shifts,
                            average_shift_length=p.average_shift_length,
                            toi=p.toi, ev_toi=p.ev_toi, pp_toi=p.pp_toi, sh_toi=p.sh_toi
                        ))
                    for s in psh:
                        shifts.append(Shift(game_id=game_id, shift_number=s.shift_num, period=s.period_num,
                                            shift_start_elapsed=s.shift_start_elapsed,
                                            shift_end_elapsed=s.shift_end_elapsed,
                                            shift_start_remaining=s.shift_start_remaining,
                                            shift_end_remaining=s.shift_end_remaining,
                                            duration=s.duration, event_string=s.event_string))
                    game_summary = gs
                    break

            if game_summary is not None:
                _roster.append(GamePlayerAssociation(team_id=team_id, game_id=game_id, jersey_num=jersey_num,
                                                     position=position, captain_status=captain_status,
                                                     player_name=name, period_toi_summaries=period_toi_summaries,
                                                     num_shifts=game_summary.num_shifts,
                                                     average_shift_length=game_summary.average_shift_length,
                                                     toi=game_summary.toi, ev_toi=game_summary.ev_toi,
                                                     pp_toi=game_summary.pp_toi,
                                                     sh_toi=game_summary.sh_toi, shifts=shifts))
            else:
                _roster.append(GamePlayerAssociation(team_id=team_id, game_id=game_id, jersey_num=jersey_num,
                                                     position=position, captain_status=captain_status,
                                                     player_name=name))

        return _roster

    def _build_rosters(self):
        self._rosters = []
        self._rosters += self._build_roster(self.nhl_roster.home_names, self.nhl_roster.home_positions,
                                            self.nhl_roster.home_jersey_numbers, self.nhl_roster.home_captain_status,
                                            self.nhl_home_toi_reports, self.game_id, self.home_team_id)
        self._rosters += self._build_roster(self.nhl_roster.away_names, self.nhl_roster.away_positions,
                                            self.nhl_roster.away_jersey_numbers, self.nhl_roster.away_captain_status,
                                            self.nhl_away_toi_reports, self.game_id, self.away_team_id)
        self._game._roster = self._rosters

    @staticmethod
    def _build_scratch(names, positions, jersey_numbers, types, captain_status, game_id, team_id):
        _scratch = []
        for name, position, jersey_num, scratch_type, captain_status in zip(names, positions, jersey_numbers,
                                                                            types, captain_status):
            _scratch.append(Scratch(team_id=team_id, game_id=game_id, jersey_num=jersey_num,
                                    position=position, captain_status=captain_status, scratch_type=scratch_type))
        return _scratch

    def _build_scratches(self):
        self._scratches = []
        self._scratches += self._build_scratch(self.nhl_roster.home_scratch_names,
                                               self.nhl_roster.home_scratch_positions,
                                               self.nhl_roster.home_scratch_jersey_numbers,
                                               self.nhl_roster.home_scratch_types,
                                               self.nhl_roster.home_scratch_captain_status, self.game_id,
                                               self.home_team_id)
        self._scratches += self._build_scratch(self.nhl_roster.away_scratch_names,
                                               self.nhl_roster.away_scratch_positions,
                                               self.nhl_roster.away_scratch_jersey_numbers,
                                               self.nhl_roster.away_scratch_types,
                                               self.nhl_roster.away_scratch_captain_status, self.game_id,
                                               self.away_team_id)
        self._game._scratches = self._scratches

    @staticmethod
    def _build_players_on_ice(team_jersey_nums, team_id, rosters):
        pois = []
        for jersey_num in team_jersey_nums:
            for r in rosters:
                if r.team_id == team_id and r.jersey_num == jersey_num:
                    pois.append(PlayerOnIce(game_player_association=r))
                    break
        return pois

    def _build_events(self):
        self._plays = []

        for play in self.nhl_plays.plays:
            home_on_ice = self._build_players_on_ice(play.home_jersey_numbers, self.home_team_id, self._rosters)
            away_on_ice = self._build_players_on_ice(play.away_jersey_numbers, self.away_team_id, self._rosters)

            try:
                kwargs = {'game': self._game, 'sequence': play.sequence, 'period': play.period,
                          'strength': play.strength, 'time_elapsed': play.time_elapsed,
                          'time_remaining': play.time_remaining, 'description': play.description, 'type_str': play.type,
                          '_players_on_ice': home_on_ice + away_on_ice}

                # Need to add logic for differentiating Play Type...
                if kwargs['type_str'] in PLAY_CONSTRUCTOR_MAP:
                    self._plays.append(PLAY_CONSTRUCTOR_MAP[kwargs['type_str']](**kwargs))
                else:
                    self._plays.append(Play(**kwargs))
            except Exception as e:
                print(play)
                raise e

        self._game._plays = self._plays

    def build(self, session, season, game_type, game_num, src_path='.', ignore_existing=True):
        """
        Safely load in an NHL HTML reports game, and generate database objects.
        :param session: SQLAlchemy session
        :param season: Integer season (end-date year)
        :param game_type: 1 - Preseason, 2 - Regular Season, 3 - Playoffs
        :param game_num: Unique season game ID, according to NHL counter
        :param src_path: Source directory of NHL.com HTML reports (if pre-downloaded).
        :return: None
        """

        #
        # Set factory variables
        #
        self.session = session
        self.season = season
        self.game_type = game_type
        self.game_num = game_num
        self.src_path = src_path

        #
        # Build game information
        #
        self.game_id = self.build_game_id(self.season, self.game_type, self.game_num)

        if ignore_existing:
            if len(self.session.query(Game).filter(Game.game_id == self.game_id).all()):
                return

        try:
            self._build_nhl_info()
        except AttributeError:
            print('Game {0} DNE'.format(self.game_id))
            return

        self._build_team_ids()
        self._build_game_obj()
        self._build_linesmen()
        self._build_officials()
        self._build_rosters()
        self._build_scratches()
        self._build_events()

        session.merge(self._game)
