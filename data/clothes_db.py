import datetime
import sqlalchemy
from sqlalchemy import DateTime, Column, String, Integer, Boolean, ForeignKey
from .db_session import SqlAlchemyBase


class Clothes(SqlAlchemyBase):
    __tablename__ = 'clothes'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    pic = sqlalchemy.Column(sqlalchemy.String)
    av_sizes = sqlalchemy.Column(sqlalchemy.String)
    sex = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)
    remaining = sqlalchemy.Column(sqlalchemy.Integer)
