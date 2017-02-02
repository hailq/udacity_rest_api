from flask import Flask, render_template, g, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meetneat.db'

db = SQLAlchemy(app)
redis = Redis()
auth = HTTPBasicAuth()


# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'NOT FOUND'}), 404)


@auth.verify_password
def verify_password(username_or_token, password):
    from app.models.user import User

    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        usr = User.query.filter_by(id=user_id).one()
    else:
        usr = User.query.filter_by(username=username_or_token).first()
        if not usr or not usr.verify_password(password):
            return False
    g.user = usr
    return True


# Rate limiting
def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


from app.resources import user
from app.resources import request
from app.resources import proposal
from app.resources import date
from app.resources import auth


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/clientOAuth')
def start():
    return render_template('clientOAuth.html')
