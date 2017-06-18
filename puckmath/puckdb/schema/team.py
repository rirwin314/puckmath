from sqlalchemy import Column, String

from .base import Base


class Team(Base):
    """

    """
    __tablename__ = 'team'

    team_abbr = Column(String, primary_key=True)
    team_name = Column(String)
