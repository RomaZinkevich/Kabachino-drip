import datetime
import sqlalchemy
from sqlalchemy import DateTime, Column, String, Integer, Boolean, ForeignKey
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(UserMixin, SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String)
    liked = sqlalchemy.Column(sqlalchemy.String)
    carted = sqlalchemy.Column(sqlalchemy.String)
    status = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return '<User {}>'.format(self.login)
