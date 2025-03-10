from datetime import date, datetime, timezone, timedelta
from typing import Dict, List, Optional
import uuid
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

categories = sa.Table(
    'categories',
    db.metadata,
    sa.Column('category_id', sa.Integer, sa.ForeignKey('category.id'),
              primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('product.id'),
              primary_key=True)
)


class BasketProduct(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица Many-To-Many продуктов в корзине. """
    __tablename__ = 'basket_products'

    basket_id: so.Mapped[int] = so.mapped_column(db.Integer, db.ForeignKey(
        'basket.id'), primary_key=True)
    product_id: so.Mapped[int] = so.mapped_column(db.Integer, db.ForeignKey(
        'product.id'), primary_key=True)
    amount: so.Mapped[int] = so.mapped_column(db.Integer, default=1)


class Role(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица role. """
    __tablename__ = 'role'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True,
                                            index=True)
    users: so.Mapped[List['User']] = so.relationship(back_populates='role')


class User(UserMixin, db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица user. """
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
    banned: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
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
    user_reviews: so.Mapped[List['Review']] = so.relationship(
        back_populates='user')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_role()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password: str) -> None:
        """ Метод генерации хэша пароля. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """ Метод проверки пароля.  """
        return check_password_hash(self.password_hash, password)

    def set_role(self, role_name: str = 'user') -> None:
        """ Назначение роли.

        Пример использования:
        >>> user = User()
        >>> user.set_role('admin')
        """
        role = db.session.scalar(sa.select(Role).where(Role.name == role_name))
        if role is None:  # В базе отсутствует роль, необходимая для работы
            role = Role(name=role_name)
            db.session.add(role)
            db.session.commit()
        self.role = role

    def get_basket(self) -> 'Basket':
        """ Получение актуальной корзины покупателя, если таковой нету,
         то создаётся новая.

        Возвращает:
            Basket: Активная корзина пользователя.
        """
        active_baskets = db.session.scalars(
            sa.select(Basket)
            .where(Basket.user_id == self.id)
            .where(Basket.active.is_(True))
            .order_by(Basket.created_at)).all()
        if not active_baskets:  # Корзина отсутствует
            basket = Basket(user_id=self.id, active=True)
            db.session.add(basket)
            db.session.commit()
        else:
            basket = active_baskets[-1]
        return basket

    @property
    def is_active(self):
        """Проверка доступа пользователя в систему."""
        return not self.banned


class Product(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица product. """
    __tablename__ = 'product'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                            unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    price: so.Mapped[int] = so.mapped_column()
    rating: so.Mapped[float] = so.mapped_column(nullable=True)
    brand: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(40), nullable=True, default=None)
    stock: so.Mapped[int] = so.mapped_column(default=0)
    photo_path: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    categories: so.Mapped[List['Category']] = so.relationship(
        secondary=categories,
        back_populates='products')
    baskets: so.Mapped[List['Basket']] = so.relationship(
        secondary='basket_products',
        back_populates='products')
    reviews: so.Mapped[List['Review']] = so.relationship(
        back_populates='product', order_by='Review.id.desc()')

    def __repr__(self):
        return '<Product {}>'.format(self.name)

    def get_path(self) -> Optional[str]:
        """ Получение пути к изображению продукта. """
        return self.photo_path

    def update_rating(self):
        """Обновление рейтинга товара."""
        reviews = self.reviews
        self.rating = round((sum(review.rating for review in reviews)
                             / len(reviews)), 2)


class Review(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица review. """
    __tablename__ = 'review'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    review: so.Mapped[str] = so.mapped_column(sa.String(140), nullable=True)
    rating: so.Mapped[int] = so.mapped_column()
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Product.id),
                                                  index=True)
    user: so.Mapped[User] = so.relationship(back_populates='user_reviews')
    product: so.Mapped[Product] = so.relationship(back_populates='reviews')


class Category(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица category. """
    __tablename__ = 'category'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    products: so.Mapped[List['Product']] = so.relationship(
        secondary=categories,
        back_populates='categories')

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Basket(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица basket. """
    __tablename__ = 'basket'
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

    def get_basket_products(self) -> Dict['Product', int]:
        """ Получение количества товаров в корзине.

        Возвращает:
            Dict[Product, int]: Словарь, где ключ — продукт,
              а значение — количество.
        """
        basket_items = dict()

        # Получаем все записи BasketProduct и связанные с ними продукты
        basket_products = db.session.execute(
            sa.select(BasketProduct, Product)
            .join(Product, BasketProduct.product_id == Product.id)
            .where(BasketProduct.basket_id == self.id)
            .order_by(Product.id.desc())
        ).all()
        for basket_product, product in basket_products:
            if self.active:  # Корзина изменяется только если активна
                # Если в наличии меньшее количество товара, чем в корзине
                if basket_product.amount > product.stock:
                    basket_product.amount = product.stock
                # Если количество товара в корзине равно нулю
                if not basket_product.amount:
                    db.session.delete(basket_product)
                db.session.commit()
            basket_items[product] = basket_product.amount

        return basket_items

    def get_total_amount(self,
                         basket_items: Optional[Dict['Product', int]] = None
                         ) -> int:
        """ Получение суммарной стоимости всех товаров в корзине.

        Если ранее был получен словарь, содержащий количество товаров
         в корзине(get_basket_products), то его можно передать в качестве
          аргумента и не пересчитывать.

        Возвращает:
            int: Суммарная стоимость товаров в корзине.
        """
        basket_items = basket_items or self.get_basket_products()
        return sum(product.price * amount
                   for product, amount in basket_items.items())

    def get_shipment_date(self):
        """Расчёт даты доставки.
        В текущей версии дата рассчитывается как сегодняшний день + 7 дней
        """
        return date.today() + timedelta(days=7)


class Order(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица order. """
    __tablename__ = 'order'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    order_number: so.Mapped[int] = so.mapped_column(
        sa.String(40), unique=True,
        index=True, default=lambda: str(uuid.uuid4())
    )
    created_at: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    shipment_date: so.Mapped[Optional[date]] = so.mapped_column()
    status_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('order_status.id'), index=True)
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(60))
    total_amount: so.Mapped[int] = so.mapped_column()
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    basket_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey(Basket.id), nullable=True)
    status: so.Mapped['OrderStatus'] = so.relationship(back_populates='orders')
    customer: so.Mapped[User] = so.relationship(back_populates='user_orders')
    basket: so.Mapped[Optional['Basket']] = so.relationship(
        back_populates='order')

    def __init__(self, *args, status_name: str = 'Создан', **kwargs):
        super().__init__(*args, **kwargs)
        self.set_status(status_name)

    def set_status(self, status_name: str = 'Создан') -> None:
        """ Назначение роли.

        Пример использования:
        >>> order = Order()
        >>> order.set_status('Создан')
        """
        status = db.session.scalar(sa.select(OrderStatus).where(
            OrderStatus.name == status_name))
        if status is None:  # В базе отсутствует статус, необходимый для работы
            status = OrderStatus(name=status_name)
            db.session.add(status)
            db.session.commit()
        self.status = status


class OrderStatus(db.Model):  # type: ignore[name-defined]
    """ Модель БД таблица order_status. """
    __tablename__ = 'order_status'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    orders: so.Mapped[List['Order']] = so.relationship(back_populates='status')

    def __repr__(self):
        return '<OrderStatus {}>'.format(self.name)

    def __str__(self):
        return self.name


@login.user_loader
def load_user(id: str) -> Optional[User]:
    """ Загрузка пользователя для Flask-Login. """
    return db.session.get(User, int(id))
