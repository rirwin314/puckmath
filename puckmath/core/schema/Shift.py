from datetime import time

from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from .Base import Base


class Shift(Base):
    """

    """
    __tablename__ = 'shift'

    id = Column(Integer, primary_key=True)

    game_id = Column(String, ForeignKey('game.game_id'))
    game = relationship('Game', uselist=False, foreign_keys=[game_id])

    game_player_association_id = Column(Integer, ForeignKey('game_player_association.id'))
    game_player_association = relationship('GamePlayerAssociation', uselist=False,
                                           foreign_keys=[game_player_association_id])
    player = relationship('Player', secondary='game_player_association')

    shift_number = Column(Integer)
    period = Column(Integer)

    shift_start_elapsed = Column(Time)
    shift_end_elapsed = Column(Time)

    shift_start_remaining = Column(Time)
    shift_end_remaining = Column(Time)

    duration = Column(Time)

    event_string = Column(String)