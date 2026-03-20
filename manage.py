import os

from dotenv import load_dotenv
from src.app import create_app

load_dotenv()


class DevUserMiddleware:
    """
    Em desenvolvimento, injeta Id/email no ambiente WSGI (como antes).
    Em produção não altera nada. Desative com DISABLE_DEV_USER_MIDDLEWARE=1.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if os.getenv('FLASK_ENV') == 'production':
            return self.app(environ, start_response)
        if os.getenv('DISABLE_DEV_USER_MIDDLEWARE', '').lower() in (
            '1',
            'true',
            'yes',
        ):
            return self.app(environ, start_response)
        environ.setdefault(
            'Id',
            os.getenv('DEV_MOCK_USER_ID', '1'),
        )
        environ.setdefault(
            'email',
            os.getenv('DEV_MOCK_USER_EMAIL', 'hrpbs@teste.com'),
        )
        return self.app(environ, start_response)


app = create_app()
app.wsgi_app = DevUserMiddleware(app.wsgi_app)

if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')
