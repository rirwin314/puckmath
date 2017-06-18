import sqlalchemy
import sqlalchemy.orm

from .Base import Base


class Coach(Base):
    """

    """
    __tablename__ = 'coach'

    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)

    # games = sqlalchemy.orm.relationship('Game')
    def __repr__(self):
        return 'Coach({0})'.format(self.name)