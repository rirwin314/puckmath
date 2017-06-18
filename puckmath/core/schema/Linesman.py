from sqlalchemy import Column, Integer, String, ForeignKey
from .Base import Base


class Linesman(Base):
    """

    """
    __tablename__ = 'linesman'

    name = Column(String, primary_key=True)

    def __repr__(self):
        return 'Linesman({0})'.format(self.name)