import os

import sqlalchemy as sa
import sqlalchemy.orm as so
from gevent.pywsgi import WSGIServer

from app import create_app, db
from app.models import Product, User, categories

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Создание контекста для работы в cli."""
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Product': Product,
            'categories': categories}


if __name__ == '__main__':
    # Debug/Development
    # app.run(debug=True, host="0.0.0.0", port="5000")
    # Production
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))

    # Production
    http_server = WSGIServer((host, port), app)
    print(f"Server running on http://{host}:{port}")
    http_server.serve_forever()
