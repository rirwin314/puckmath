import re

from sqlalchemy import Column, Integer, String, ForeignKey, Time, Enum, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .base import Base
from puckmath.puckdb.builder.utils import format_team_abbr
from puckmath.puckdb.nhl_parser.utils import text_to_time


PLAY_ENUM = Enum('PSTR', 'FAC', 'STOP', 'HIT', 'SHOT', 'MISS', 'GIVE', 'GOAL', 'BLOCK',
                 'PEND', 'PENL', 'TAKE', 'GEND', 'SOC', 'GOFF', 'EISTR', 'EIEND', name='play_enum')
ZONE_ENUM = Enum('Neu. Zone', 'Def. Zone', 'Off. Zone', '', name='zone_enum')
SHOT_ENUM = Enum('Wrist', 'Snap', 'Slap', 'Tip-In', 'Backhand', 'Deflected', 'Wrap-around', '', name='shot_enum')
MISS_ENUM = Enum('Wide of Net', 'Goalpost', 'Over Net', 'Hit Crossbar', '', name='miss_enum')
PENALTY_ENUM = Enum(name='penalty_enum')
PENALTY_SHOT_STR = ' Penalty Shot,'


class PlayerOnIce(Base):
    """

    """
    __tablename__ = 'player_on_ice'

    id = Column(Integer, primary_key=True)

    play_id = Column(Integer, ForeignKey('play.id'))
    play = relationship('Play', uselist=False, foreign_keys=[play_id])

    game_player_association_id = Column(Integer, ForeignKey('game_player_association.id'))
    game_player_association = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[game_player_association_id])
    # player = relationship('Player', secondary='game_player_association')


class Play(Base):
    """

    """
    __tablename__ = 'play'
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'play'
    }

    id = Column(Integer, primary_key=True)

    type = Column(String)
    type_str = Column(String)

    game_id = Column(String, ForeignKey('game.game_id'))
    game = relationship('Game', uselist=False, foreign_keys=[game_id])

    sequence = Column(Integer)
    period = Column(Integer)

    strength = Column(String)
    time_elapsed = Column(Time)
    time_remaining = Column(Time)

    description = Column(String)

    _players_on_ice = relationship('PlayerOnIce')

    @hybrid_property
    def home_on_ice(self):
        return [pl for pl in self._players_on_ice if pl.game_player_association.team_id == self.game.home_team_id]

    @hybrid_property
    def away_on_ice(self):
        return [pl for pl in self._players_on_ice if pl.game_player_association.team_id == self.game.away_team_id]

    def __repr__(self):
        return '#{0} - Period {1} - {2} [{3}]'.format(
            self.sequence, self.period, self.description, self.time_elapsed)

    def match_player_on_ice(self, jersey_num, team_id):
        return self.match_player_on_roster(jersey_num, team_id)
        # for pl in self._players_on_ice:
        #     gpa = pl.game_player_association
        #     if gpa.team_id == team_id and gpa.jersey_num == jersey_num:
        #         return gpa
        # return None

    def match_player_on_roster(self, jersey_num, team_id):
        for gpa in self.game._roster:
            if gpa.team_id == team_id and gpa.jersey_num == jersey_num:
                return gpa
        return None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.description = str(re.sub(' +', ' ', self.description))


class PeriodStart(Play):
    """

    """
    __tablename__ = 'period_start'
    __mapper_args__ = {
        'polymorphic_identity': 'period_start'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    period_start_time = Column(Time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _tm_str = self.description.split(' ')[-2]
        self.period_start_time = text_to_time(_tm_str)


class PeriodEnd(Play):
    """

    """
    __tablename__ = 'period_end'
    __mapper_args__ = {
        'polymorphic_identity': 'period_end'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    period_end_time = Column(Time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _tm_str = self.description.split(' ')[-2]
        self.period_end_time = text_to_time(_tm_str)


class GameEnd(Play):
    """

    """
    __tablename__ = 'game_end'
    __mapper_args__ = {
        'polymorphic_identity': 'game_end'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    game_end_time = Column(Time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _tm_str = self.description.split(' ')[-2]
        self.game_end_time = text_to_time(_tm_str)


class ShootoutCompleted(Play):
    """

    """
    __tablename__ = 'shootout_completed'
    __mapper_args__ = {
        'polymorphic_identity': 'shootout_completed'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    shootout_end_time = Column(Time)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        _tm_str = self.description.split(' ')[-2]
        self.shootout_end_time = text_to_time(_tm_str)


class FaceOff(Play):
    """

    """
    __tablename__ = 'face_off'
    __mapper_args__ = {
        'polymorphic_identity': 'face_off'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    home_player_association_id = Column(Integer, ForeignKey('game_player_association.id'))
    away_player_association_id = Column(Integer, ForeignKey('game_player_association.id'))

    home_player_association = relationship('GamePlayerAssociation', uselist=False,
                                           foreign_keys=[home_player_association_id])
    away_player_association = relationship('GamePlayerAssociation', uselist=False,
                                           foreign_keys=[away_player_association_id])

    zone = Column(ZONE_ENUM)
    winning_team = Column(String, ForeignKey('team.team_abbr'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        splits = self.description.split(' ')
        try:
            self.winning_team = format_team_abbr(splits[0])
        except:
            self.winning_team = None

        home_team_id = format_team_abbr(self.description.split('#')[1].strip().split(' ')[-1])
        away_team_id = format_team_abbr(self.description.split('#')[0].strip().split(' ')[-1])
        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]
        away_jersey_num = int(self.description.split('#')[1].strip().split(' ')[0])
        home_jersey_num = int(self.description.split('#')[2].strip().split(' ')[0])

        self.home_player_association = self.match_player_on_ice(home_jersey_num, home_team_id)
        self.away_player_association = self.match_player_on_ice(away_jersey_num, away_team_id)


class Stoppage(Play):
    __tablename__ = 'stoppage'
    __mapper_args__ = {
        'polymorphic_identity': 'stoppage'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    @hybrid_property
    def reason(self):
        return self.description


class Hit(Play):
    __tablename__ = 'hit'
    __mapper_args__ = {
        'polymorphic_identity': 'hit'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)
    zone = Column(ZONE_ENUM)

    hitter_id = Column(Integer, ForeignKey('game_player_association.id'))
    hitter = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[hitter_id],
                          backref='hits_given')

    hittee_id = Column(Integer, ForeignKey('game_player_association.id'))
    hittee = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[hittee_id],
                          backref='hits_taken')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]

        try:
            hitter_team = format_team_abbr(self.description.strip().split(' ')[0])
            hitter_num = int(self.description.split('#')[1].strip().split(' ')[0])
            self.hitter = self.match_player_on_ice(hitter_num, hitter_team)
        except ValueError:
            self.hitter = None

        try:
            hittee_team = format_team_abbr(self.description.strip().split('#')[1].strip().split(' ')[-1])
            hittee_num = int(self.description.strip().split('#')[2].strip().split(' ')[0])
            self.hittee = self.match_player_on_ice(hittee_num, hittee_team)
        except ValueError:
            self.hittee = None


class Shot(Play):
    """

    """
    __tablename__ = 'shot'
    __mapper_args__ = {
        'polymorphic_identity': 'shot'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    shooter_id = Column(Integer, ForeignKey('game_player_association.id'))
    shooter = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[shooter_id],
                           backref='shots')

    shot_type = Column(SHOT_ENUM)
    zone = Column(ZONE_ENUM)
    distance = Column(Integer)

    is_penalty_shot = Column(Boolean)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.is_penalty_shot = PENALTY_SHOT_STR in self.description

        if self.is_penalty_shot:
            self.description = self.description.replace(PENALTY_SHOT_STR, '')

        shooter_team = format_team_abbr(self.description.split(' ')[0])
        if '#' in self.description:
            shooter_num = int(self.description.split('#')[1].split(' ')[0])
        else:
            shooter_num = re.search('[0-9]+', self.description).group()
        self.shooter = self.match_player_on_ice(shooter_num, shooter_team)

        self.shot_type = [s for s in SHOT_ENUM.enums if s in self.description][0]
        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]
        self.distance = int(self.description.strip().split(' ')[-2])


class Miss(Play):
    """

    """
    __tablename__ = 'miss'
    __mapper_args__ = {
        'polymorphic_identity': 'miss'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    shooter_id = Column(Integer, ForeignKey('game_player_association.id'))
    shooter = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[shooter_id],
                           backref='misses')

    shot_type = Column(SHOT_ENUM)
    miss_type = Column(MISS_ENUM)
    zone = Column(ZONE_ENUM)
    distance = Column(Integer)

    is_penalty_shot = Column(Boolean)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.is_penalty_shot = PENALTY_SHOT_STR in self.description

        if self.is_penalty_shot:
            self.description = self.description.replace(PENALTY_SHOT_STR, '')

        shooter_team = format_team_abbr(self.description.split(' ')[0])
        try:
            shooter_num = int(self.description.split('#')[1].split(' ')[0])
            self.shooter = self.match_player_on_ice(shooter_num, shooter_team)
        except ValueError:
            shooter_num = -1
            self.shooter = None

        self.miss_type = [m for m in MISS_ENUM.enums if m in self.description][0]
        self.shot_type = [s for s in SHOT_ENUM.enums if s in self.description][0]
        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]
        self.distance = int(self.description.split(' ft.')[0].strip().split()[-1])


class Block(Play):
    """

    """
    __tablename__ = 'block'
    __mapper_args__ = {
        'polymorphic_identity': 'block'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    shooter_id = Column(Integer, ForeignKey('game_player_association.id'))
    shooter = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[shooter_id],
                           backref='shots_blocked')

    blocker_id = Column(Integer, ForeignKey('game_player_association.id'))
    blocker = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[blocker_id],
                           backref='blocks')

    shot_type = Column(SHOT_ENUM)
    zone = Column(ZONE_ENUM)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            shooter_team = format_team_abbr(self.description.split(' ')[0])
            shooter_num = int(self.description.split('#')[1].split(' ')[0].strip())
            self.shooter = self.match_player_on_ice(shooter_num, shooter_team)
        except AssertionError:
            self.shooter = None

        try:
            blocker_team = format_team_abbr(self.description.split('#')[1].split(' ')[-2].strip())
            blocker_num = int(self.description.split('#')[2].split(' ')[0].strip())
            self.blocker = self.match_player_on_ice(blocker_num, blocker_team)
        except AssertionError:
            self.blocker = None

        self.shot_type = [s for s in SHOT_ENUM.enums if s in self.description][0]
        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]


class Goal(Play):
    """

    """
    __tablename__ = 'goal'
    __mapper_args__ = {
        'polymorphic_identity': 'goal'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    scorer_id = Column(Integer, ForeignKey('game_player_association.id'))
    scorer = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[scorer_id],
                          backref='goals')

    primary_assist_id = Column(Integer, ForeignKey('game_player_association.id'))
    primary_assist = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[primary_assist_id],
                                  backref='primary_assists')

    secondary_assist_id = Column(Integer, ForeignKey('game_player_association.id'))
    secondary_assist = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[secondary_assist_id],
                                    backref='secondary_assists')

    shot_type = Column(SHOT_ENUM)
    zone = Column(ZONE_ENUM)
    distance = Column(Integer)

    is_penalty_shot = Column(Boolean)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.is_penalty_shot = PENALTY_SHOT_STR in self.description

        if self.is_penalty_shot:
            self.description = self.description.replace(PENALTY_SHOT_STR, '')

        scorer_team = format_team_abbr(self.description.split(' ')[0])
        scorer_num = int(self.description.split('#')[1].split(' ')[0].strip())
        self.scorer = self.match_player_on_roster(scorer_num, scorer_team)

        try:
            primary_assist_num = int(self.description.split('#')[2].split(' ')[0].strip())
            self.primary_assist = self.match_player_on_roster(primary_assist_num, scorer_team)
        except IndexError:
            self.primary_assist = None

        try:
            secondary_assist_num = int(self.description.split('#')[3].split(' ')[0].strip())
            self.secondary_assist = self.match_player_on_roster(secondary_assist_num, scorer_team)
        except IndexError:
            self.secondary_assist = None

        self.shot_type = [s for s in SHOT_ENUM.enums if s in self.description][0]
        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]
        self.distance = int(self.description.split(' ft.')[0].strip().split()[-1])


class GiveAway(Play):
    """

    """
    __tablename__ = 'give_away'
    __mapper_args__ = {
        'polymorphic_identity': 'give_away'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    giver_id = Column(Integer, ForeignKey('game_player_association.id'))
    giver = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[giver_id],
                         backref='give_aways')

    zone = Column(ZONE_ENUM)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        team = format_team_abbr(self.description.split(' ')[0])
        num = int(self.description.split('#')[1].strip().split(' ')[0])
        self.giver = self.match_player_on_ice(num, team)

        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]


class TakeAway(Play):
    """

    """
    __tablename__ = 'take_away'
    __mapper_args__ = {
        'polymorphic_identity': 'take_away'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    taker_id = Column(Integer, ForeignKey('game_player_association.id'))
    taker = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[taker_id],
                         backref='take_aways')

    zone = Column(ZONE_ENUM)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        team = format_team_abbr(self.description.split(' ')[0])
        num = int(self.description.split('#')[1].strip().split(' ')[0])
        self.taker = self.match_player_on_ice(num, team)

        self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]


class Penalty(Play):
    """

    """
    __tablename__ = 'penalty'
    __mapper_args__ = {
        'polymorphic_identity': 'penalty'
    }

    id = Column(Integer, ForeignKey('play.id'), primary_key=True)

    offender_team = Column(String, ForeignKey('team.team_abbr'))
    offender_id = Column(Integer, ForeignKey('game_player_association.id'))
    offender = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[offender_id],
                            backref='penalties')

    # penalty_type = Column(PENALTY_ENUM)
    penalty_type = Column(String)
    duration = Column(Integer)

    zone = Column(ZONE_ENUM)

    drawer_id = Column(Integer, ForeignKey('game_player_association.id'))
    drawer = relationship('GamePlayerAssociation', uselist=False, foreign_keys=[drawer_id],
                          backref='penalties_drawn')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self.offender_team = format_team_abbr(self.description.split(' ')[0].strip())
        except AssertionError:
            tm = None
            offender_num = int(self.description.split('#')[1].split(' ')[0])
            try:
                self.offender = self.match_player_on_roster(offender_num, self.game.home_team_id)
                self.offender_team = self.game.home_team_id
            except ValueError:
                self.offender = self.match_player_on_roster(offender_num, self.game.away_team_id)
                self.offender_team = self.game.away_team_id

        try:
            self.duration = int(self.description.split('(')[1].split(' ')[0])
        except ValueError:
            self.duration = None

        if 'TEAM ' not in self.description.upper() and ' PS ' not in self.description:
            try:
                offender_num = int(self.description.split('#')[1].split(' ')[0])
                self.offender = self.match_player_on_roster(offender_num, self.offender_team)
            except ValueError:
                self.offender = None

            if 'Drawn' in self.description:
                drawer_team = format_team_abbr(self.description.split('Drawn By: ')[1].strip().split()[0])
                try:
                    drawer_num = int(self.description.split('Drawn By: ')[1].strip().split('#')[1].strip().split()[0])
                    self.drawer = self.match_player_on_roster(drawer_num, drawer_team)
                except ValueError:
                    self.drawer = None

            self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]

            # self.penalty_type = self.description.split(self.offender.player_name.split(' ')[-1].upper())[1].strip().split('(')[0]
            penalty_type = []
            for s in self.description.split('(')[0].split():
                if not s.isupper() and not sum([c.isdigit() for c in s]):
                    penalty_type.append(s)
            self.penalty_type = ' '.join(penalty_type)
        elif ' PS ' not in self.description:
            self.zone = [z for z in ZONE_ENUM.enums if z in self.description][0]


PLAY_CONSTRUCTOR_MAP = {
    'FAC': FaceOff,
    'PSTR': PeriodStart,
    'PEND': PeriodEnd,
    'GEND': GameEnd,
    'SOC': ShootoutCompleted,
    'STOP': Stoppage,
    'HIT': Hit,
    'SHOT': Shot,
    'MISS': Miss,
    'BLOCK': Block,
    'GOAL': Goal,
    'GIVE': GiveAway,
    'TAKE': TakeAway,
    'PENL': Penalty,
    'GOFF': Play
}
