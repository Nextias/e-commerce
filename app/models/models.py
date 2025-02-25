from datetime import datetime, timezone, date
from hashlib import md5
from time import time
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app, session
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
    sa.Column('amount', sa.Integer, default=1)
)


class BacketProduct(db.Model):
    __tablename__ = 'backet_products'

    backet_id = db.Column(db.Integer, db.ForeignKey(
        'backet.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), primary_key=True)
    amount = db.Column(db.Integer, default=1)


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
    user_backets: so.Mapped[List['Backet']] = so.relationship(
        back_populates='user', order_by='Backet.created_at'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_role(self, role_name='user'):
        role = db.session.scalar(sa.select(Role).where(Role.name == role_name))
        if role:
            self.role = role

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def get_backet(self):
        active_backets = db.session.scalars(sa.select(Backet)
                                            .where(Backet.user_id == self.id)
                                            .where(Backet.active)
                                            .order_by(Backet.created_at)).all()
        print(active_backets, type(active_backets))
        if not active_backets:
            backet = Backet(user_id=self.id, active=True)
            db.session.add(backet)
            db.session.commit()
        else:
            backet = active_backets[0]
        return backet


class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                            unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    price: so.Mapped[int] = so.mapped_column()
    brand: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(40), nullable=True, default=None)
    stock: so.Mapped[int] = so.mapped_column(default=0)
    photo_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
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
        secondary='backet_products',
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

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Backet(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    products: so.Mapped[List['Product']] = so.relationship(
        secondary='backet_products',
        back_populates='backets'
    )
    user: so.Mapped[User] = so.relationship(back_populates='user_backets')
    order: so.Mapped[Optional['Order']] = so.relationship(
        back_populates='backet')

    def get_backet_products(self):
        backet_items = dict()
        if self.products:
            for product in self.products:
                backet_item = db.session.scalar(
                    sa.select(BacketProduct).where(
                        BacketProduct.backet_id == self.id,
                        BacketProduct.product_id == product.id))
                backet_items[product] = backet_item.amount
        return backet_items

    def get_total_amount(self, backet_items=None):
        backet_items = backet_items or self.get_backet_products()
        return sum(product.price * amount
                   for product, amount in backet_items.items())


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
    backet_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey(Backet.id), nullable=True)

    products: so.Mapped[List['Product']] = so.relationship(
        secondary='order_products',
        back_populates='orders'
    )
    customer: so.Mapped[User] = so.relationship(back_populates='user_orders')
    backet: so.Mapped[Optional['Backet']] = so.relationship(
        back_populates='order')

    def generate_order_number(self):
        pass


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
