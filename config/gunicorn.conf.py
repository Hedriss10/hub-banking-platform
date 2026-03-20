"""
Configuração do Gunicorn (WSGI). Fica em `config/` para não misturar com código da app.

Sobreposição opcional: GUNICORN_BIND, GUNICORN_WORKERS.
"""
import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _project_root)

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8001')
workers = int(os.environ.get('GUNICORN_WORKERS', '4'))
threads = 2
timeout = 60
preload_app = True
accesslog = '-'
errorlog = '-'
loglevel = 'info'
