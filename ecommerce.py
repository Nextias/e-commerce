import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import Product, User, categories

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """ Создание контекста для работы в cli. """
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Product': Product,
            'categories': categories}


if __name__ == '__main__':
    app.run()
