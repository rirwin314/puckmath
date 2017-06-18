import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Time
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.hybrid import hybrid_property

from .Base import Base


class PeriodTOISummary(Base):
    """

    """
    __tablename__ = 'period_toi_summary'

    id = Column(Integer, primary_key=True)

    game_player_association_id = Column(Integer, ForeignKey('game_player_association.id'))

    period_num = Column(Integer)

    toi = Column(Time)
    ev_toi = Column(Time)
    pp_toi = Column(Time)
    sh_toi = Column(Time)

    num_shifts = Column(Integer)
    average_shift_length = Column(Time)


class GamePlayerAssociation(Base):
    """

    """
    __tablename__ = 'game_player_association'

    id = Column(Integer, primary_key=True)

    player_name = Column(String)

    team_id = Column(String, ForeignKey('team.team_abbr'))
    team = sqlalchemy.orm.relationship('Team', uselist=False, foreign_keys=[team_id])

    game_id = Column(String, ForeignKey('game.game_id'))
    game = sqlalchemy.orm.relationship('Game', uselist=False, foreign_keys=[game_id])

    player_id = Column(String, ForeignKey('player.player_id'))
    player = sqlalchemy.orm.relationship('Player', uselist=False, foreign_keys=[player_id])

    jersey_num = Column(Integer)
    position = Column(String)

    captain_status = Column(Enum('C', 'A', '', name='captain_status'), default='')

    num_shifts = Column(Integer)
    average_shift_length = Column(Time)
    toi = Column(Time)
    ev_toi = Column(Time)
    pp_toi = Column(Time)
    sh_toi = Column(Time)

    period_toi_summaries = sqlalchemy.orm.relationship('PeriodTOISummary', order_by='PeriodTOISummary.period_num',
                                                       collection_class=ordering_list('period_num'),
                                                       cascade="save-update, merge, delete, delete-orphan")
    shifts = sqlalchemy.orm.relationship('Shift', order_by='Shift.shift_number',
                                         collection_class=ordering_list('shift_number'),
                                         cascade="save-update, merge, delete, delete-orphan")

    home_faceoffs = sqlalchemy.orm.relationship(
        'FaceOff',
        primaryjoin='GamePlayerAssociation.id==FaceOff.home_player_association_id')
    away_faceoffs = sqlalchemy.orm.relationship(
        'FaceOff',
        primaryjoin='GamePlayerAssociation.id==FaceOff.away_player_association_id')

    won_faceoffs = sqlalchemy.orm.relationship(
        'FaceOff',
        primaryjoin='and_(or_(GamePlayerAssociation.id==FaceOff.home_player_association_id, '
                    'GamePlayerAssociation.id==FaceOff.away_player_association_id), '
                    'FaceOff.winning_team==GamePlayerAssociation.team_id)')
    lost_faceoffs = sqlalchemy.orm.relationship(
        'FaceOff',
        primaryjoin='and_(or_(GamePlayerAssociation.id==FaceOff.home_player_association_id, '
                    'GamePlayerAssociation.id==FaceOff.away_player_association_id), '
                    'FaceOff.winning_team!=GamePlayerAssociation.team_id)')

    def __repr__(self):
        return '{0} - #{1} {2} {3}, {4} -- {5}'.format(self.team_id, self.jersey_num, self.player_name,
                                                       self.captain_status, self.position, self.toi)
