import unittest

from flask import url_for

from app import create_app, db
from app.models import OrderStatus, Role, User, Product
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
        return self.client.post(
            url_for('admin.create_product'),
            data=dict(name=name, description=description, price=price,
                      brand=brand, stock=stock),
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
        # Предполагается наличие полей формы
        self.assertIn('Управление товарами', response.data.decode('utf-8'))
        self.assertIn('ID', response.data.decode('utf-8'))
        self.assertIn('Name', response.data.decode('utf-8'))
        self.assertIn('Brand', response.data.decode('utf-8'))
        self.assertIn('Stock', response.data.decode('utf-8'))

    def test_create_product_loads(self):
        """Проверка страницы добавления продуктов."""

    def test_edit_stock(self):
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

    def test_create_product(self):
        response = self.create_product('product', 'description', 1000, 'brand',
                                       20)
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие нового товара в управлении товарами
        self.assertIn('Управление товарами', response.data.decode('utf-8'))
        self.assertIn('product', response.data.decode('utf-8'))
        self.assertIn('1000', response.data.decode('utf-8'))
        self.assertIn('brand', response.data.decode('utf-8'))
        self.assertIn('20', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
