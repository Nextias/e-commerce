from datetime import datetime, timezone, date
from hashlib import md5
from time import time
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
from app import db, login


categories = sa.Table(
    'categories',
    db.metadata,
    sa.Column('category_id', sa.Integer, sa.ForeignKey('category.id'),
              primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
              primary_key=True)
)

order_products = sa.Table(
    'order_products',
    db.metadata,
    sa.Column('order_id', sa.Integer, sa.ForeignKey('order.id'),
              primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
              primary_key=True),
)

backet_products = sa.Table(
    'backet_products',
    db.metadata,
    sa.Column('backet_id', sa.Integer, sa.ForeignKey('backet.id'),
              primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
              primary_key=True),
)


class Role(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(20), index=True)
    users: so.Mapped[List['User']] = so.relationship(back_populates='role')


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
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Role.id),
                                               index=True)
    role: so.Mapped[Role] = so.relationship(back_populates='users')
    user_orders: so.Mapped[List['Order']] = so.relationship(
        back_populates='customer')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_role(self, role='user'):
        query = sa.select(Role).where(Role.name == role)
        self.role_id = db.session.scalar(query).id

    # def get_orders(self):
    #     query = self.user_orders.select().order_by(Order.id)
    #     return db.session.scalars(query)

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
    categories: so.Mapped[List['Category']] = so.relationship(
        secondary=categories,
        primaryjoin='Product.id == categories.c.product_id',
        secondaryjoin='Category.id == categories.c.category_id',
        back_populates='products')
    orders: so.Mapped[List['Order']] = so.relationship(
        secondary=order_products,
        back_populates='products'
    )
    backets: so.Mapped[List['Backet']] = so.relationship(
        secondary=backet_products,
        back_populates='products'
    )

    def __repr__(self):
        return '<Product {}>'.format(self.name)

    def get_path(self):
        pass


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    products: so.Mapped[List['Product']] = so.relationship(
        secondary=categories,
        primaryjoin='Category.id == categories.c.category_id',
        secondaryjoin='Product.id == categories.c.product_id',
        back_populates='categories')

    def get_products(self):
        query = self.products.select()
        return db.session.scalars(query)

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Order(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_number: so.Mapped[int] = so.mapped_column(unique=True, index=True)
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    shipment_date: so.Mapped[Optional[date]] = so.mapped_column()
    status: so.Mapped[str] = so.mapped_column(sa.String(10))
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    total_amount: so.Mapped[int] = so.mapped_column()
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    products: so.Mapped[List['Product']] = so.relationship(
        secondary=order_products,
        back_populates='orders'
    )
    customer: so.Mapped[User] = so.relationship(back_populates='user_orders')

    def generate_order_number(self):
        pass


class Backet(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    active: so.Mapped[str] = so.mapped_column(sa.Boolean, default=True)
    products: so.Mapped[List['Product']] = so.relationship(
        secondary=backet_products,
        back_populates='backets'
    )


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
