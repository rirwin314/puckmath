from sqlalchemy import Column, Integer, String, ForeignKey, Time, Enum, DateTime, inspect
from sqlalchemy.orm import relationship
import sqlalchemy.ext.hybrid
from .base import Base
from .linesman import Linesman
from .official import Official


class GameLinesmanAssociation(Base):
    """

    """
    __tablename__ = 'game_linesman_association'

    id = Column(Integer, primary_key=True)

    linesman_id = Column(String, ForeignKey('linesman.name'))
    game_id = Column(String, ForeignKey('game.game_id'))

    linesman_jersey = Column(Integer)


class GameOfficialAssociation(Base):
    """

    """
    __tablename__ = 'game_official_association'

    id = Column(Integer, primary_key=True)

    official_id = Column(String, ForeignKey('official.name'))
    game_id = Column(String, ForeignKey('game.game_id'))

    official_jersey = Column(Integer)


class Game(Base):
    """

    """
    __tablename__ = 'game'

    game_id = Column(String, primary_key=True)
    game_type = Column(Enum('Preseason', 'Regular', 'Playoffs', name='game_type'), default='Regular')

    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)

    attendance = Column(Integer)
    venue = Column(String)

    home_team_id = Column(String, ForeignKey('team.team_abbr'))
    home_team = relationship('Team', uselist=False, foreign_keys=[home_team_id])

    away_team_id = Column(String, ForeignKey('team.team_abbr'))
    away_team = relationship('Team', uselist=False, foreign_keys=[away_team_id])

    home_goals = Column(Integer)
    away_goals = Column(Integer)

    game_remarks = Column(String)
    overtimes = Column(String)

    game_duration = Column(Time)

    home_coach_id = Column(String, ForeignKey('coach.name'))
    home_coach = relationship('Coach', uselist=False, foreign_keys=[home_coach_id])

    away_coach_id = Column(String, ForeignKey('coach.name'))
    away_coach = relationship('Coach', uselist=False, foreign_keys=[away_coach_id])

    _roster = relationship('GamePlayerAssociation', cascade="save-update, merge, delete, delete-orphan")
    _scratches = relationship('Scratch', cascade="save-update, merge, delete, delete-orphan")
    _officials = relationship('GameOfficialAssociation', cascade="save-update, merge, delete, delete-orphan")
    _linesmen = relationship('GameLinesmanAssociation', cascade="save-update, merge, delete, delete-orphan")
    _plays = relationship('Play', cascade="save-update, merge, delete, delete-orphan")

    @sqlalchemy.ext.hybrid.hybrid_property
    def home_roster(self):
        return [r for r in self._roster if r.team_id == self.home_team_id]

    @sqlalchemy.ext.hybrid.hybrid_property
    def away_roster(self):
        return [r for r in self._roster if r.team_id == self.away_team_id]

    @sqlalchemy.ext.hybrid.hybrid_property
    def home_scratches(self):
        return [s for s in self._scratches if s.team_id == self.home_team_id]

    @sqlalchemy.ext.hybrid.hybrid_property
    def away_scratches(self):
        return [s for s in self._scratches if s.team_id == self.away_team_id]

    @sqlalchemy.ext.hybrid.hybrid_property
    def home_score(self):
        return sum([1 for p in self._plays if p.type_str == 'GOAL' and p.scorer.team_id == self.home_team_id])

    @sqlalchemy.ext.hybrid.hybrid_property
    def away_score(self):
        return sum([1 for p in self._plays if p.type_str == 'GOAL' and p.scorer.team_id == self.away_team_id])

    def __repr__(self):
        return '{2} -- {0} @ {1} ({3})'.format(self.away_team_id, self.home_team_id, self.start_datetime, self.venue)
