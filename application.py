import flask
import flask_sqlalchemy

from celery import Celery
from views.client import (
    ClientFormResource,
    ClientResourceCreate,
    ClientResourceDelete,
    ClientResourceIndex,
    ResponseResource,
)


class Route(object):

    def __init__(self, url, route_name, resource):
        self.url = url
        self.route_name = route_name
        self.resource = resource


handlers = [
    Route('/', 'client.index', ClientResourceIndex),
    Route('/client', 'client.create', ClientResourceCreate),
    Route('/client/<int:id>/delete',
          'client.delete', ClientResourceDelete),
    Route('/client/new', 'client.new', ClientFormResource),
    Route('/sms', 'sendsms', ResponseResource)
]


class Application(object):

    def __init__(self, routes, config, debug=True):
        self.flask_app = flask.Flask(__name__)
        self.routes = routes
        self.debug = debug
        self._configure_app(config)
        self._set_routes()

    def celery(self):
        app = self.flask_app
        celery = Celery(app.import_name, broker=app.config[
                        'CELERY_BROKER_URL'])
        celery.conf.update(app.config)

        TaskBase = celery.Task

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        celery.Task = ContextTask

        return celery

    def _set_routes(self):
        for route in self.routes:
            app_view = route.resource.as_view(route.route_name)
            self.flask_app.add_url_rule(route.url, view_func=app_view)

    def _configure_app(self, env):
        celery_url = env.get('CELERY_URL')

        self.flask_app.config[
            'SQLALCHEMY_DATABASE_URI'] = env.get('DATABASE_URL')

        self.flask_app.config['CELERY_BROKER_URL'] = env.get(
            'REDIS_URL', celery_url)
        self.flask_app.config['CELERY_RESULT_BACKEND'] = env.get(
            'REDIS_URL', celery_url)

        self.flask_app.config['TWILIO_ACCOUNT_SID'] = env.get(
            'TWILIO_ACCOUNT_SID')
        self.flask_app.config['TWILIO_AUTH_TOKEN'] = env.get(
            'TWILIO_AUTH_TOKEN')
        self.flask_app.config['TWILIO_NUMBER'] = env.get('TWILIO_NUMBER')

        self.flask_app.secret_key = env.get('SECRET_KEY')

        self.db = flask_sqlalchemy.SQLAlchemy(self.flask_app)

    def start_app(self):
        self.flask_app.run(debug=self.debug)
