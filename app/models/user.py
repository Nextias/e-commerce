from datetime import datetime, timezone
from hashlib import md5
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
from app import db, login

class User(UserMixin, db.Model):
    """ Модель БД таблица user"""
    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    state: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    zip_code: so.Mapped[Optional[str]] = so.mapped_column(sa.String(40))
    country: so.Mapped[Optional[str]]
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
