from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

from . import register as register, login as login, logout as logout
