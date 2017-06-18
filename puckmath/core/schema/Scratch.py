from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .Base import Base


class Scratch(Base):
    """

    """
    __tablename__ = 'game_scratch_assoc'

    id = Column(Integer, primary_key=True)

    team_id = Column(String, ForeignKey('team.team_abbr'))
    team = relationship('Team', uselist=False, foreign_keys=[team_id])

    game_id = Column(String, ForeignKey('game.game_id'))
    player_id = Column(String, ForeignKey('player.player_id'))

    scratch_type = Column(Enum('INJURED', 'HEALTHY', name='scratch_type'), default='HEALTHY')

    captain_status = Column(Enum('C', 'A', '', name='captain_status'), default='')

    position = Column(String)
    jersey_num = Column(Integer)
