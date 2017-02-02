from app import app, db, auth
from app.models.user import User
from flask import request, jsonify, abort, g

from app.utils.rate_limit import ratelimit


@app.route('/api/v1/users', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_user():
    return get_all_users()


@app.route('/api/v1/users/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_one_user(id):
    user = User.query.filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'status': 'OK', 'data': user.serialize})


@app.route('/api/v1/users', methods=['POST'])
@ratelimit(limit=180, per=60)
def post_user():
    return create_new_user()


@app.route('/api/v1/users', methods=['PUT'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def put_user():
    user = User.query.filter_by(id=g.user.id).one()

    if not user:
        abort(400)

    new_password = request.json.get('password')
    new_email = request.json.get('email')
    new_picture = request.json.get('picture')

    if new_password is not None:
        user.hash_password(new_password)
    if new_email is not None:
        user.email = new_email
    if new_picture is not None:
        user.picture = new_picture

    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'User updated successfully'}), 200


@app.route('/api/v1/users', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def delete_user():
    user = User.query.filter_by(id=g.user.id).one()

    if not user:
        abort(400)

    db.session.delete(user)
    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'User deleted successfully'}), 200


def get_all_users():
    users = User.query.all()
    return jsonify({'status': 'OK', 'data': [i.serialize for i in users]})


def create_new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({'status': 'Error', 'message': 'Missing arguments'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'message': 'user already exists'
        }), 200

    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'username': user.username
    }), 201
