import unittest

from app import create_app, db
from flask import url_for
from app.models import Role, User
from config import TestConfig


class TestAuthRoutes(unittest.TestCase):

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
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.commit()

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

    def test_login_page_loads(self):
        """Проверка загрузки страницы авторизации."""
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('remember_me', response.data.decode('utf-8'))

    def test_register_page_loads(self):
        """Проверка загрузки страницы регистрации."""
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('password', response.data.decode('utf-8'))
        self.assertIn('Зарегистрироваться', response.data.decode('utf-8'))

    def test_register_with_valid_data(self):
        """Проверка регистрации с валидными данными."""
        response = self.register_user(
            'newuser', 'newuser@example.com', 'newpassword')
        self.assertEqual(response.status_code, 200)
        # Предполагается, что произойдёт перенаправление на авторизацию
        self.assertIn('remember_me', response.data.decode('utf-8'))
        # Проверка пользователя в базе
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user, "Пользователь не был создан.")

    def test_register_with_existing_username(self):
        """Проверка повторной регистрации по занятому username."""
        self.register_user('existinguser', 'existing@example.com', 'password')
        # Попытка повторной регистрации с таким же username
        response = self.register_user(
            'existinguser', 'another@example.com', 'password')
        self.assertEqual(response.status_code, 200)
        # Предполагается, что форма не пройдёт валидацию
        self.assertIn('<div class="invalid-feedback">',
                      response.data.decode('utf-8'))

    def test_register_with_existing_email(self):
        """Проверка повторной регистрации по занятому email."""
        self.register_user('existinguser', 'existing@example.com', 'password')
        # Попытка повторной регистрации с таким же email
        response = self.register_user(
            'anotheruse', 'existing@example.com', 'password')
        self.assertEqual(response.status_code, 200)
        # Предполагается, что форма не пройдёт валидацию
        self.assertIn('<div class="invalid-feedback">',
                      response.data.decode('utf-8'))

    def test_login_with_valid_credentials(self):
        """Проверка авторизации с валидными данными."""
        self.register_user('testuser', 'test@example.com', 'password')

        # Проверка авторизации
        response = self.login_user('testuser', 'password')
        self.assertEqual(response.status_code, 200)
        # Предполагается, что /logout есть на странице
        self.assertIn('/logout', response.data.decode('utf-8'))

    def test_login_with_invalid_credentials(self):
        """Проверка авторизации с невалидными данными."""
        response = self.login_user('wronguser', 'wrongpassword')
        self.assertEqual(response.status_code, 200)
        # Предполагается, что /logout нет на странице
        self.assertNotIn('/logout', response.data.decode('utf-8'))

    def test_login_with_remember_me(self):
        """Проверка авторизации с remember_me=True."""
        self.register_user('testuser', 'test@example.com', 'password')

        # Авторизация с remember_me
        response = self.login_user('testuser', 'password', remember_me=True)
        self.assertEqual(response.status_code, 200)
        # Предполагается, что /logout есть на странице
        self.assertIn('/logout', response.data.decode('utf-8'))

    def test_logout(self):
        """Провека выхода пользователя через /logout"""
        # Регистрация а аутентификация пользователя
        self.register_user('testuser', 'test@example.com', 'password')
        self.login_user('testuser', 'password')
        # Выход через logout
        response = self.client.get(
            url_for('auth.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Предполагается, что /login есть на странице
        self.assertIn('/login', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
