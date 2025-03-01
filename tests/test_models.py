import unittest

from app import create_app, db
from app.models import (Basket, Category, Order, OrderStatus,
                        Product, Role, User)
from sqlalchemy.exc import IntegrityError
from config import TestConfig


def create_example_user():
    """ Создание примера пользователя. """
    user = User(username='testuser', email='testuser@example.com',
                address='test address', first_name='test firstname',
                last_name='test lastname', about_me='test about me',
                phone_number='test phone number')
    user.set_password('password123')  # Установка пароля пользователю

    # Добавление пользователя в базу
    db.session.add(user)
    db.session.commit()
    return user


def create_example_product():
    """ Создание примера товара. """
    product = Product(name='product', description='description',
                      price=10, photo_path='path', stock=20)
    db.session.add(product)
    db.session.commit()
    return product


def create_example_basket():
    """ Создание примера корзины с товаром. """
    # Создаём пользователя
    user = create_example_user()
    db.session.add(user)
    # Создаем товар
    product = create_example_product()
    db.session.add(product)
    # Создаем корзину
    basket = user.get_basket()
    basket.products.append(product)
    db.session.add(basket)
    db.session.commit()
    return basket


def create_example_order():
    """ Создание примера заказа с товаром. """
    basket = create_example_basket()
    # Создаём заказ
    status = OrderStatus(name='status')
    db.session.add(status)
    db.session.commit()
    order = Order(order_number=111, status_name=status.name, total_amount=0,
                  user_id=basket.user_id, basket_id=basket.id)
    db.session.add(order)
    db.session.commit()
    return order


class UserModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Тест создания пользователя. """
        # Создание нового пользователя
        user = create_example_user()

        # Получение созданного пользователя из базы
        retrieved_user = User.query.filter_by(username='testuser').first()

        # Проверка, что пользователь был создан корректно
        self.assertIsNotNone(retrieved_user, "Пользователь не был создан.")
        self.assertEqual(retrieved_user.username, user.username,
                         "username не совпадает.")
        self.assertEqual(retrieved_user.email,
                         user.email, "email не совпадает.")
        self.assertEqual(retrieved_user.role.name,
                         user.role.name, "role не совпадают.")
        self.assertEqual(retrieved_user.first_name,
                         user.first_name, "first_name не совпадают.")
        self.assertEqual(retrieved_user.last_name,
                         user.last_name, "lastname_name не совпадают.")
        self.assertEqual(retrieved_user.about_me,
                         user.about_me, "about_me не совпадают.")

    def test_password_hashing(self):
        """ Проверка хеширования паролей. """
        u = User(username='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_duplicate_username(self):
        """Проверка, что программа не позволяет создать двух пользователей
          с одинаковым никнеймом.
        """
        # Создаем первого пользователя
        create_example_user()

        # Ожидаем, что это вызовет исключение
        with self.assertRaises(IntegrityError):  # Ловим IntegrityError
            # Пытаемся создать второго пользователя с тем же никнеймом
            create_example_user()

        # Сбрасываем состояние сессии после исключения
        db.session.rollback()
        # Проверяем, что в DB один пользователь с этим никнеймом
        users_with_same_username = User.query.filter_by(
            username='testuser').count()
        self.assertEqual(users_with_same_username, 1, "В базе данных больше"
                         "одного пользователя с одинаковым никнеймом."
                         )

    def test_get_basket(self):
        """ Проверка получения корзины пользователя. """
        # Создаем пользователя
        user = create_example_user()

        # Создаем активную корзину
        basket = Basket(user_id=user.id)
        db.session.add(basket)
        db.session.commit()

        # Создаём неактивную корзину
        basket2 = Basket(user_id=user.id, active=False)
        db.session.add(basket2)
        db.session.commit()

        # Получаем актуальную корзину пользователя
        retrieved_basket = user.get_basket()
        self.assertEqual(retrieved_basket.id, basket.id)

        # Проверяем, что функция создаст новую корзину, если активных нет
        basket.active = False
        db.session.commit()
        retrieved_basket = user.get_basket()
        self.assertNotIn(retrieved_basket, (None, basket, basket2))


class RoleModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_role_creation(self):
        """ Тест создания роли. """
        # Создания роли
        role = Role(name='role')
        # Добавление роли в базу
        db.session.add(role)
        db.session.commit()

        # Получение созданного пользователя из базы
        retrieved_role = Role.query.filter_by(name='role').first()

        # Проверка, что пользователь был создан корректно
        self.assertIsNotNone(retrieved_role, "Роль не была создана.")
        self.assertEqual(retrieved_role.name, 'role',
                         "username не совпадает.")

    def test_set_role(self):
        # Создания роли
        role = Role(name='role')
        db.session.add(role)
        db.session.commit()

        # Создаем пользователя
        user1 = create_example_user()

        # Назначаем роль
        user1.set_role(role.name)
        db.session.commit()

        # Проверка соответствия роли
        self.assertEqual(user1.role_id, role.id)

    def test_get_users_by_role(self):
        # Создаем роль
        role = Role(name='role')
        db.session.add(role)
        db.session.commit()

        # Создаем пользователя
        user1 = create_example_user()
        user1.set_password('password123')
        db.session.add(user1)
        db.session.commit()

        # Назначаем роль
        user1.set_role(role.name)

        # Проверяем наличие user1 в списке пользователей с ролью
        users = role.users
        self.assertEqual(len(users), 1)
        self.assertIn(user1, users)


class CategoryModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_creation(self):
        """ Проверка создания категории. """
        # Создание категории
        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()

        # Получение категории из базы данных
        retrieved_category = Category.query.filter_by(
            name='Test Category').first()

        # Проверка, что категория была создана корректно
        self.assertIsNotNone(retrieved_category, "Категория не была создана.")
        self.assertEqual(retrieved_category.name,
                         'Test Category', "name не совпадает.")

    def test_get_products_by_category(self):
        """ Проверка получения продуктов по категории. """
        # Создаем категорию
        category = Category(name='category')
        db.session.add(category)
        db.session.commit()

        # Создаем товар
        product = Product(name='product', description='description',
                          price=10, categories=[category])
        db.session.add(product)
        db.session.commit()
        # Проверяем наличие product в продуктах по категории
        products = category.products
        self.assertEqual(len(products), 1)
        self.assertIn(product, products)


class ProductModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_product_creation(self):
        """Проверка создания продукта."""
        # Создаем товар
        product = create_example_product()

        # Получение продукта из базы данных
        retrieved_product = Product.query.filter_by(
            name=product.name).first()

        # Проверка, что продукт был создан корректно
        self.assertIsNotNone(retrieved_product, "Продукт не был создан.")
        self.assertEqual(retrieved_product.name,
                         product.name, "name не совпадает.")
        self.assertEqual(retrieved_product.description,
                         product.description, "description не совпадает.")
        self.assertEqual(retrieved_product.price,
                         product.price, "price не совпадает.")
        self.assertEqual(retrieved_product.stock,
                         product.stock, "stock не совпадает.")
        self.assertEqual(retrieved_product.photo_path,
                         product.photo_path, "photo_path не совпадает.")

    def test_get_categories_by_product(self):
        """ Проверка получения категорий продукта. """
        # Создаем категорию
        category = Category(name='category')
        db.session.add(category)
        db.session.commit()

        # Создаем товар
        product = create_example_product()
        product.categories = [category]
        db.session.commit()
        # Проверяем наличие категории в категориях продукта
        retrieved_categories = product.categories
        self.assertIn(category, retrieved_categories)

    def test_get_baskets_by_product(self):
        """ Проверка получения корзин по продукту. """
        # Создаём корзину
        basket = create_example_basket()
        # Получаем продукт
        product = basket.products[0]
        # Проверяем получение корзин по продукту
        baskets = product.baskets
        self.assertIn(basket, baskets)

    def test_get_path(self):
        """ Проверка метода get_path """
        product = create_example_product()
        product.photo_path = 'path'
        db.session.commit()
        retrievew_path = product.get_path()
        self.assertEqual(retrievew_path, product.photo_path)


class BasketModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_basket_creation(self):
        """Проверка создания корзины."""
        # Создаем корзину
        user = create_example_user()
        basket = Basket(user_id=user.id)
        db.session.add(basket)
        db.session.commit()
        # Получение корзины из базы данных
        retrieved_basket = Basket.query.filter_by(
            user_id=user.id).first()

        # Проверка, что корзина была создана корректно
        self.assertIsNotNone(retrieved_basket, "Корзина не была создана.")
        self.assertEqual(retrieved_basket.user_id,
                         user.id, "user_id не совпадает.")
        self.assertEqual(retrieved_basket.active,
                         basket.active, "active не совпадает.")

    def test_get_user(self):
        """Проверка получения пользователя по корзине."""
        # Создаем корзину
        user = create_example_user()
        basket = Basket(user_id=user.id)
        db.session.add(basket)
        db.session.commit()
        # Получаем пользователя
        retrieved_user = basket.user
        # Проверка полученного пользователя
        self.assertEqual(retrieved_user.id, user.id)

    def test_products_by_basket(self):
        """Проверка продуктов по корзине."""
        # Создаем корзину
        user = create_example_user()
        basket = Basket(user_id=user.id)
        db.session.add(basket)
        db.session.commit()

        # Добавляем товар в корзину
        product = create_example_product()
        basket.products.append(product)
        db.session.commit()

        # Получаем продукты из корзины
        products = basket.products

        # Проверка полученного пользователя
        self.assertIn(product, products)
        self.assertEqual(len(products), 1)

    def test_get_order(self):
        """Проверка получения заказа по корзине."""
        # Создаем корзину
        user = create_example_user()
        basket = Basket(user_id=user.id)
        db.session.add(basket)
        db.session.commit()

        # Создаём заказ
        status = OrderStatus(name='status')
        db.session.add(status)
        db.session.commit()
        order = Order(order_number=111, status_name=status.name,
                      total_amount=0, user_id=basket.user_id,
                      basket_id=basket.id)
        db.session.add(order)
        db.session.commit()

        # Получаем заказ по корзине
        retrieved_order = basket.order

        # Проверка полученного пользователя
        self.assertEqual(retrieved_order.id, order.id)
        self.assertEqual(retrieved_order.order_number, order.order_number)


class OrderModelCase(unittest.TestCase):
    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_order_creation(self):
        """Проверка создания заказа."""
        # Создаем корзину
        basket = create_example_basket()
        # Создаём заказ
        status = OrderStatus(name='status')
        db.session.add(status)
        db.session.commit()
        order = Order(order_number=111, status_name=status.name,
                      total_amount=0, user_id=basket.user_id,
                      basket_id=basket.id)
        db.session.add(order)
        db.session.commit()

        # Получение заказа из базы данных
        retrieved_order = Order.query.filter_by(
            order_number=order.order_number).first()

        # Проверка, что заказ был создан корректно
        self.assertIsNotNone(retrieved_order, "Заказ не был создан.")
        self.assertEqual(retrieved_order.order_number,
                         order.order_number, "order_number не совпадает.")
        self.assertEqual(retrieved_order.status_id,
                         order.status_id, "status_id не совпадает.")
        self.assertEqual(retrieved_order.total_amount,
                         order.total_amount, "total_amount не совпадает.")
        self.assertEqual(retrieved_order.user_id,
                         order.user_id, "user_id не совпадает.")
        self.assertEqual(retrieved_order.basket_id,
                         order.basket_id, "basket_id не совпадает.")

    def test_get_status(self):
        """Проверка получения статуса заказа."""
        # Создаем корзину
        basket = create_example_basket()
        # Создаём заказ
        status = OrderStatus(name='status')
        db.session.add(status)
        db.session.commit()
        order = Order(order_number=111, status_name=status.name,
                      total_amount=0, user_id=basket.user_id,
                      basket_id=basket.id)
        db.session.add(order)
        db.session.commit()
        # Получаем статус заказа
        retrieved_status = order.status
        self.assertEqual(retrieved_status.id, status.id)

    def test_get_customer(self):
        """ Проверка получения покупателя по заказу. """
        # Создаем корзину
        basket = create_example_basket()
        # Создаём заказ
        status = OrderStatus(name='status')
        db.session.add(status)
        db.session.commit()
        order = Order(order_number=111, status_name=status.name,
                      total_amount=0, user_id=basket.user_id,
                      basket_id=basket.id)
        db.session.add(order)
        db.session.commit()
        # Получаем покупателя по заказу
        retrieved_user = order.customer
        self.assertEqual(retrieved_user.id, basket.user_id)

    def test_get_basket(self):
        """ Проверка получения корзины по заказу. """
        # Создаем корзину
        basket = create_example_basket()
        # Создаём заказ
        status = OrderStatus(name='status')
        db.session.add(status)
        db.session.commit()
        order = Order(order_number=111, status_name=status.name,
                      total_amount=0, user_id=basket.user_id,
                      basket_id=basket.id)
        db.session.add(order)
        db.session.commit()
        # Получаем покупателя по заказу
        retrieved_basket = order.basket
        self.assertEqual(retrieved_basket.id, basket.id)


if __name__ == '__main__':
    unittest.main(verbosity=2)
