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

# wishlist = sa.Table(
#     'wishlist',
#     db.metadata,
#     sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'),
#               primary_key=True),
#     sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
#               primary_key=True)
# )

categories = sa.Table(
    'categories',
    db.metadata,
    sa.Column('category_id', sa.Integer, sa.ForeignKey('category.id'),
              primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
              primary_key=True)
)


class User(UserMixin, db.Model):
    """ Модель БД таблица user"""
    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    phone_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                            unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    price: so.Mapped[int] = so.mapped_column()
    photo_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    categories: so.WriteOnlyMapped['Category'] = so.relationship(
        secondary=categories,
        primaryjoin="Product.id == categories.c.product_id",
        secondaryjoin="Category.id == categories.c.category_id",
        back_populates='products')

    def get_categories(self):
        query = self.categories.select()
        return db.session.scalars(query)

    def __repr__(self):
        return '<Product {}>'.format(self.name)

    def get_path(self):
        pass


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    products: so.WriteOnlyMapped['Product'] = so.relationship(
        secondary=categories,
        primaryjoin="Category.id == categories.c.category_id",
        secondaryjoin="Product.id == categories.c.product_id",
        back_populates='categories')

    def get_products(self):
        query = self.products.select()
        return db.session.scalars(query)
    
    def __repr__(self):
        return '<Category {}>'.format(self.name)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
