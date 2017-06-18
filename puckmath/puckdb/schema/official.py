from sqlalchemy import Column, Integer, String, ForeignKey

import sqlalchemy.orm

from .base import Base


class Official(Base):
    """

    """
    __tablename__ = 'official'

    name = Column(String, primary_key=True)

    def __repr__(self):
        return 'Official({0})'.format(self.name)