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


class BasketProduct(db.Model):
    """ Модель БД таблица Many-To-Many продуктов в корзине. """
    __tablename__ = 'basket_products'

    basket_id = db.Column(db.Integer, db.ForeignKey(
        'basket.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), primary_key=True)
    amount = db.Column(db.Integer, default=1)


class Role(db.Model):
    """ Модель БД таблица role. """
    __tablename__ = 'role'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True,
                                            index=True)
    users: so.Mapped[List['User']] = so.relationship(back_populates='role')


class User(UserMixin, db.Model):
    """ Модель БД таблица user. """
    __tablename__ = 'user'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_role()

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
        back_populates='customer', order_by='desc(Order.id)')
    user_baskets: so.Mapped[List['Basket']] = so.relationship(
        back_populates='user', order_by='Basket.created_at'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """ Метод генерации хэша пароля. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Метод проверки пароля.  """
        return check_password_hash(self.password_hash, password)

    def set_role(self, role_name='user'):
        """ Назначение роли. """
        role = db.session.scalar(sa.select(Role).where(Role.name == role_name))
        if role:
            self.role = role

    def get_basket(self):
        """ Получение актуальной корзины покупателя, если таковой нету,
         то создаётся новая.
        """
        active_baskets = db.session.scalars(sa.select(Basket)
                                            .where(Basket.user_id == self.id)
                                            .where(Basket.active == True)
                                            .order_by(Basket.created_at)).all()
        if not active_baskets:  # Корзина отсутствует
            print('create basket')
            basket = Basket(user_id=self.id, active=True)
            db.session.add(basket)
            db.session.commit()
        else:
            basket = active_baskets[-1]
        return basket


class Product(db.Model):
    """ Модель БД таблица product. """
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
    baskets: so.Mapped[List['Basket']] = so.relationship(
        secondary='basket_products',
        back_populates='products'
    )

    def __repr__(self):
        return '<Product {}>'.format(self.name)

    def get_path(self):
        pass


class Category(db.Model):
    """ Модель БД таблица category. """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    products: so.Mapped[List['Product']] = so.relationship(
        secondary=categories,
        primaryjoin='Category.id == categories.c.category_id',
        secondaryjoin='Product.id == categories.c.product_id',
        back_populates='categories')

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Basket(db.Model):
    """ Модель БД таблица basket. """
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    products: so.Mapped[List['Product']] = so.relationship(
        secondary='basket_products',
        back_populates='baskets'
    )
    user: so.Mapped[User] = so.relationship(back_populates='user_baskets')
    order: so.Mapped[Optional['Order']] = so.relationship(
        back_populates='basket')

    def get_basket_products(self):
        """ Получение количества товаров в корзине.
        Если в корзине количество определённого товара было уменьшено до нуля,
          то товар удаляется из корзины.
        Если количество товара в корзине больше, чем товара в наличии,
            то количество корректируетсяю
        """
        basket_items = dict()
        if self.products:
            for product in self.products:
                basket_item = db.session.scalar(
                    sa.select(BasketProduct).where(
                        BasketProduct.basket_id == self.id,
                        BasketProduct.product_id == product.id))
                # Если в наличии меньшее количество товара, чем в корзине
                if basket_item.amount > product.stock:
                    basket_item.amount = product.stock
                # Если количество товара в корзине равно нулю
                if not basket_item.amount:
                    db.session.delete(basket_item)
                db.session.commit()
                basket_items[product] = basket_item.amount
        return basket_items

    def get_total_amount(self, basket_items=None):
        """ Получение суммарной стоимости всех товаров в корзине.
        Если ранее был получен словарь, содержащий количество товаров
         в корзине(get_basket_products), то его можно передать в качестве
          аргумента и не пересчитывать.
        """
        basket_items = basket_items or self.get_basket_products()
        return sum(product.price * amount
                   for product, amount in basket_items.items())


class Order(db.Model):
    """ Модель БД таблица order. """
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
    basket_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey(Basket.id), nullable=True)

    products: so.Mapped[List['Product']] = so.relationship(
        secondary='order_products',
        back_populates='orders'
    )
    customer: so.Mapped[User] = so.relationship(back_populates='user_orders')
    basket: so.Mapped[Optional['Basket']] = so.relationship(
        back_populates='order')


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
