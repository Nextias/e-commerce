import unittest

from flask import url_for

from app import create_app, db
from app.models import OrderStatus, Role, User
from config import TestConfig


class TestMainRoutes(unittest.TestCase):
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
