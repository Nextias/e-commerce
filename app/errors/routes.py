from flask import render_template

from app.errors import bp


@bp.app_errorhandler(400)
def bad_request(error):
    return render_template('errors/400.html'), 400


@bp.app_errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(502)
def bad_gateway(error):
    return render_template('errors/502.html'), 502


@bp.app_errorhandler(503)
def service_unavailable(error):
    return render_template('errors/503.html'), 503


@bp.app_errorhandler(504)
def gateway_timeout(error):
    return render_template('errors/504.html'), 504
