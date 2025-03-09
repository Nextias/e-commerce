import unittest

from flask import url_for

from app import create_app, db
from app.models import Order, OrderStatus, Product, Role, User
from config import TestConfig


class TestMainRoutes(unittest.TestCase):
    # Определения констант тестового пользователя
    USERNAME = 'user'
    EMAIL = 'user@example.com'
    PASSWORD = 'Newpassword1'

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
        product = Product(name='product', description='description',
                          price=10, photo_path='path', stock=20)
        status = OrderStatus(name='Создан')
        status2 = OrderStatus(name='Отменён')
        db.session.add(status)
        db.session.add(status2)
        db.session.add(user_role)
        db.session.add(admin_role)
        db.session.add(product)
        db.session.commit()
        self.product = product
        # Аутентификация пользователя
        self.register_user(self.USERNAME, self.EMAIL, self.PASSWORD)
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

    def add_product(self, product_id):
        """Добавить продукт в корзину пользователя."""
        return self.client.post(
            url_for('main.add_item', product_id=product_id)
        )

    def remove_product(self, product_id):
        """Удалить продукт из корзины пользователя."""
        return self.client.post(
            url_for('main.remove_item', product_id=product_id)
        )

    def submit_order(self, address):
        """Создать заказ."""
        return self.client.post(
            url_for('main.submit_order'),
            data=dict(address=address),
            follow_redirects=True
        )

    def edit_profile(self, first_name, last_name, phone_number, about_me,
                     address):
        """Редактировать профиль."""
        return self.client.post(
            url_for('main.edit_profile'),
            data=dict(first_name=first_name, last_name=last_name,
                      phone_number=phone_number, about_me=about_me,
                      address=address),
            follow_redirects=True
        )

    def proceed_to_checkout(self):
        """Подтвердить корзину и перейти к подтверждению."""
        return self.client.post(
            url_for('main.checkout'),
            follow_redirects=True
        )

    def cancel_order(self, id):
        """Отменить заказ."""
        return self.client.post(
            url_for('main.cancel_order', id=id),
            follow_redirects=True
        )

    def test_index_page_loads(self):
        """Проверка загрузки главной страницы."""
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 200)
        # Предполагается персонализированное приветствие
        self.assertIn(f', {self.USERNAME}!', response.data.decode('utf-8'))

    def test_product_page_loads(self):
        """Проверка загрузки страницы продукта."""
        response = self.client.get(url_for('main.product', id=self.product.id))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие информации о продукте
        self.assertIn(self.product.name, response.data.decode('utf-8'))
        self.assertIn(str(self.product.price), response.data.decode('utf-8'))
        self.assertIn(str(self.product.stock), response.data.decode('utf-8'))

    def test_profile_page_loads(self):
        """Проверка загрузки профиля."""
        response = self.client.get(url_for('main.profile'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие информации о пользователе
        self.assertIn(f'{self.USERNAME}', response.data.decode('utf-8'))
        self.assertIn(f'{self.EMAIL}', response.data.decode('utf-8'))

    def test_edit_profile_page_loads(self):
        """Проверка загрузки редактирования профиля."""
        response = self.client.get(url_for('main.edit_profile'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие полей формы
        self.assertIn('first_name', response.data.decode('utf-8'))
        self.assertIn('last_name', response.data.decode('utf-8'))
        self.assertIn('phone_number', response.data.decode('utf-8'))
        self.assertIn('about_me', response.data.decode('utf-8'))
        self.assertIn('address', response.data.decode('utf-8'))
        self.assertIn('submit', response.data.decode('utf-8'))

    def test_basket_page_loads(self):
        """Проверка загрузки страницы корзины."""
        response = self.client.get(url_for('main.basket'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие обязательных полей
        self.assertIn('/checkout', response.data.decode('utf-8'))
        self.assertIn('Перейти к подтверждению', response.data.decode('utf-8'))
        # Предполагается отсутствие товаров в корзине
        self.assertNotIn('amount-', response.data.decode('utf-8'))

    def test_explore_page_loads(self):
        """Проверка загрузки страницы поиска товаров."""
        response = self.client.get(url_for('main.explore'))
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие обязательных полей
        self.assertIn('amount-', response.data.decode('utf-8'))
        self.assertIn(self.product.name, response.data.decode('utf-8'))
        self.assertIn(str(self.product.price), response.data.decode('utf-8'))
        self.assertIn('Поиск товаров', response.data.decode('utf-8'))

    def test_checkout(self):
        """Проверка процесса оформления заказа."""
        # Добавляем продукт в корзину
        self.add_product(self.product.id)

        # Переходим к оформлению заказа
        response = self.proceed_to_checkout()

        # Проверяем, что страница оформления заказа загружается успешно
        self.assertEqual(response.status_code, 200)

        # Проверяем, что на странице есть необходимые элементы
        self.assertIn('address', response.data.decode('utf-8'))
        self.assertIn('shipment-date', response.data.decode('utf-8'))
        self.assertIn('/submit_order', response.data.decode('utf-8'))

        # Проверяем, что продукт присутствует на странице оформления заказа
        self.assertIn(self.product.name, response.data.decode('utf-8'))
        self.assertIn(str(self.product.price), response.data.decode('utf-8'))

    def test_order(self):
        """Проверка создания заказа и загрузки страницы заказа."""
        # Создание заказа
        self.add_product(self.product.id)
        response = self.submit_order('address')
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие данных заказа
        self.assertIn('order_status', response.data.decode('utf-8'))
        self.assertIn('total-amount', response.data.decode('utf-8'))
        self.assertIn('/product', response.data.decode('utf-8'))

    def test_cancel_order(self):
        """Проверка отмены заказа."""
        # Создание заказа
        self.add_product(self.product.id)
        self.submit_order('address')
        retrievew_order = Order.query.first()
        response = self.cancel_order(id=retrievew_order.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(retrievew_order.status.name, 'Отменён')

    def test_change_amount(self):
        """Проверка добавления/удаления единицы товара в корзину."""
        # Получаем объект пользователя
        user = User.query.filter_by(username=self.USERNAME).first()
        # Получаем корзину пользователя
        basket = user.get_basket()
        # Добавляем продукт в корзину
        response = self.add_product(self.product.id)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что продукт добавлен в корзину
        products = basket.products
        self.assertTrue(self.product in products)
        # Удаляем продукт из корзины
        response = self.remove_product(self.product.id)
        self.assertEqual(response.status_code, 200)
        # Проверяем, что продукт удалён из корзины
        products = basket.products
        self.assertTrue(self.product not in products)

    def test_edit_profile(self):
        """Проверка редактирования профиля."""
        response = self.edit_profile('edited_first_name', 'edited_last_name',
                                     '+7-800-555-35-35', 'edited_about_me',
                                     'edited_address')
        self.assertEqual(response.status_code, 200)
        # Предполагается наличие изменённых значений
        self.assertIn('edited_first_name', response.data.decode('utf-8'))
        self.assertIn('edited_last_name', response.data.decode('utf-8'))
        self.assertIn('+7-800-555-35-35', response.data.decode('utf-8'))
        self.assertIn('edited_about_me', response.data.decode('utf-8'))
        self.assertIn('edited_address', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
