import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, and_, or_

from .base import Base
from .game_player_association import GamePlayerAssociation
from .play import *


class Player(Base):
    """

    """
    __tablename__ = 'player'

    player_id = Column(String, primary_key=True)
    full_name = Column(String)

    start_year = Column(Integer)
    last_year = Column(Integer)

    position = Column(String)

    games = sqlalchemy.orm.relationship('Game', secondary='game_player_association')

    game_summaries = sqlalchemy.orm.relationship('GamePlayerAssociation')

    def __repr__(self):
        return '{0}({1}, {2}, {3}-{4})'.format(
            self.player_id, self.full_name, self.position, self.start_year, self.last_year)