import unittest

from flask import url_for

from app import create_app, db
from app.models import OrderStatus, Role, User, Product, Order
from config import TestConfig


class TestAdminRoutes(unittest.TestCase):
    # Определения констант тестового пользователя
    USERNAME = 'user'
    EMAIL = 'user@example.com'
    PASSWORD = 'newpassword'

    def setUp(self):
        # Создание объекта приложения
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        # Создание объекта DB
        db.create_all()
        # Создание необходимого для тестов пресета данных
        user_role = Role(name='user')
        admin_role = Role(name='admin')
        status = OrderStatus(name='Создан')
        status2 = OrderStatus(name='Отменён')
        db.session.add(status)
        db.session.add(status2)
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()
        # Создание и аутентификация админа
        admin_user = User(username=self.USERNAME, email=self.EMAIL)
        admin_user.set_role('admin')
        admin_user.set_password(self.PASSWORD)
        db.session.add(admin_user)
        db.session.commit()
        self.admin_user = admin_user
        self.login_user(self.USERNAME, self.PASSWORD)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self, username, email, password):
        """Регистрация пользователя"""
        return self.client.post(
            url_for('auth.register'),
            data=dict(username=username, email=email,
                      password=password, password2=password),
            follow_redirects=True
        )

    def login_user(self, username, password, remember_me=False):
        """Авторизация пользователя."""
        return self.client.post(
            url_for('auth.login'),
            data=dict(username=username, password=password,
                      remember_me=remember_me),
            follow_redirects=True
        )

    def edit_stock(self, product_id, amount):
        return self.client.post(
            url_for('admin.edit_stock', id=product_id),
            data=dict(amount=amount),
            follow_redirects=True
        )

    def create_product(self, name, description, price, brand, stock):
        """Создать продукт."""
        return self.client.post(
            url_for('admin.create_product'),
            data=dict(name=name, description=description, price=price,
                      brand=brand, stock=stock),
            follow_redirects=True
        )

    def add_product(self, product_id):
        """Добавить продукт в корзину пользователя."""
        return self.client.post(
            url_for('main.add_item', product_id=product_id)
        )

    def edit_product(self, id, name, description, price, brand):
        return self.client.post(
            url_for('admin.edit_product', id=id),
            data=dict(name=name, description=description, price=price,
                      brand=brand),
            follow_redirects=True
        )

    def delete_product(self, id):
        return self.client.post(
            url_for('admin.delete_product', id=id),
            follow_redirects=True
        )

    def submit_order(self, address):
        """Создать заказ."""
        return self.client.post(
            url_for('main.submit_order'),
            data=dict(address=address),
            follow_redirects=True
        )

    def confirm_order(self, order_number):
        """Подтвердить заказ."""
        return self.client.post(
            url_for('admin.confirm_order', order_number=order_number),
            follow_redirects=True
        )

    def finish_order(self, order_number):
        """Завершить заказ."""
        return self.client.post(
            url_for('admin.finish_order', order_number=order_number),
            follow_redirects=True
        )

    def test_admin_page_loads(self):
        """Проверка загрузки главной страницы Панели Администратора."""
        response = self.client.get(url_for('admin.admin'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей
        self.assertIn('Панель администратора', response.data.decode('utf-8'))
        self.assertIn('Товаров', response.data.decode('utf-8'))
        self.assertIn('Заказов', response.data.decode('utf-8'))
        self.assertIn('Пользователей', response.data.decode('utf-8'))

    def test_products_loads(self):
        """Проверка загрузки страницы продуктов."""
        response = self.client.get(url_for('admin.products'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей
        self.assertIn('product-table', response.data.decode('utf-8'))
        self.assertIn('ID', response.data.decode('utf-8'))
        self.assertIn('Название', response.data.decode('utf-8'))
        self.assertIn('Бренд', response.data.decode('utf-8'))
        self.assertIn('Количество', response.data.decode('utf-8'))
        self.assertIn('Наличие', response.data.decode('utf-8'))

    def test_create_product_loads(self):
        """Проверка загрузки страницы добавления продуктов."""
        response = self.client.get(url_for('admin.create_product'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей формы
        self.assertIn('Добавить товар', response.data.decode('utf-8'))
        self.assertIn('name', response.data.decode('utf-8'))
        self.assertIn('price', response.data.decode('utf-8'))
        self.assertIn('stock', response.data.decode('utf-8'))
        self.assertIn('brand', response.data.decode('utf-8'))
        self.assertIn('submit', response.data.decode('utf-8'))

    def test_edit_product_loads(self):
        """Проверка загрузки страницы редактирования продуктов."""
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        response = self.client.get(
            url_for('admin.edit_product', id=product.id))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей формы
        self.assertIn('name', response.data.decode('utf-8'))
        self.assertIn('price', response.data.decode('utf-8'))
        self.assertIn('categories', response.data.decode('utf-8'))
        self.assertIn('brand', response.data.decode('utf-8'))
        self.assertIn('Сохранить', response.data.decode('utf-8'))

    def test_orders_loads(self):
        """Проверка загрузки страницы заказов."""
        response = self.client.get(url_for('admin.orders'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей формы
        self.assertIn('order-table', response.data.decode('utf-8'))
        self.assertIn('ID', response.data.decode('utf-8'))
        self.assertIn('Номер заказа', response.data.decode('utf-8'))
        self.assertIn('Сумма', response.data.decode('utf-8'))
        self.assertIn('Дата доставки', response.data.decode('utf-8'))
        self.assertIn('Статус', response.data.decode('utf-8'))

    def test_users_loads(self):
        """Проверка загрузки страницы пользователей."""

    def test_edit_user_loads(self):
        """Проверка загрузки страницы редактирования пользователя."""

    def test_create_product(self):
        """Проверка добавления нового продукта."""
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие нового товара в управлении товарами
        self.assertIn('Управление товарами', response.data.decode('utf-8'))
        self.assertIn('product', response.data.decode('utf-8'))
        self.assertIn('1000', response.data.decode('utf-8'))
        self.assertIn('brand', response.data.decode('utf-8'))
        self.assertIn('20', response.data.decode('utf-8'))

    def test_delete_product(self):
        """Проверка удаления продукта."""
        self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        response = self.delete_product(product.id)
        self.assertEqual(response.status_code, 200)
        # Предполагается, что в базе нет товаров после удалению
        product = Product.query.first()
        self.assertTrue(product is None)

    def test_edit_stock(self):
        """Проверка изменения количества продуктов в наличии."""
        self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        # Изменяем количество товара на валидное
        self.edit_stock(product.id, 1000)
        product = Product.query.first()
        self.assertEqual(product.stock, 1000)
        # Пытаемся изменить количество товара на отрицательное
        self.edit_stock(product.id, -100)
        product = Product.query.first()
        self.assertEqual(product.stock, 1000)

    def test_edit_product(self):
        """Проверка редактирования товара."""
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        response = self.edit_product(product.id, 'product2', 'description2',
                                     1000500, 'brand2')
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие обновлённых значений в информации о товаре
        self.assertIn('Информация о товаре', response.data.decode('utf-8'))
        self.assertIn('product2', response.data.decode('utf-8'))
        self.assertIn('description2', response.data.decode('utf-8'))
        self.assertIn('1000500', response.data.decode('utf-8'))
        self.assertIn('brand2', response.data.decode('utf-8'))

    def test_confirm_order(self):
        """Проверка подтверждения заказа."""
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        self.add_product(product.id)
        self.submit_order('address')
        order = Order.query.first()
        self.assertEqual(order.status.name, 'Создан')
        response = self.confirm_order(order_number=order.order_number)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status.name, 'Подтверждён')

    def test_finish_order(self):
        """Проверка завершения заказа."""
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        product = Product.query.first()
        self.add_product(product.id)
        self.submit_order('address')
        order = Order.query.first()
        self.assertEqual(order.status.name, 'Создан')
        self.confirm_order(order_number=order.order_number)
        response = self.finish_order(order_number=order.order_number)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status.name, 'Завершён')

    def test_edit_user(self):
        """Проверка редактирования пользователя."""

    def test_ban_user(self):
        """Проверка блокировки пользователя."""

    def test_delete_user(self):
        """Проверка удаления пользователя."""


if __name__ == '__main__':
    unittest.main()
