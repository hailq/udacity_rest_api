from app import app, db, auth
from app.models.request import Request
from app.models.proposal import Proposal
from flask import request, jsonify, abort, g
from sqlalchemy import or_

from app.utils.rate_limit import ratelimit


@app.route('/api/v1/proposals', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_proposal():
    return get_all_proposal()


@app.route('/api/v1/proposals/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_one_proposal(id):
    proposal = Proposal.query \
        .filter_by(id=id) \
        .filter(or_(Proposal.user_proposed_to == g.user.id, Proposal.user_proposed_from == g.user.id)) \
        .first()

    if not proposal:
        return jsonify({'status': 'Not found', 'data': None}), 404
    return jsonify({'status': 'OK', 'data': proposal.serialize})


@app.route('/api/v1/proposals', methods=['POST'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def post_proposal():
    return create_new_proposal()


@app.route('/api/v1/proposals/<int:id>', methods=['PUT'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def put_proposal(id):
    proposal = Proposal.query \
        .filter_by(id=id) \
        .filter_by(user_proposed_from=g.user.id) \
        .first()

    if not proposal:
        abort(400)

    new_filled = request.json.get('filled')

    if new_filled is not None:
        proposal.filled = new_filled

    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Proposal updated successfully'}), 200


@app.route('/api/v1/proposals/<int:id>', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def delete_proposal(id):
    proposal = Proposal.query \
        .filter_by(id=id) \
        .filter_by(user_proposed_from=g.user.id) \
        .first()

    if not proposal:
        abort(400)

    db.session.delete(proposal)
    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Proposal deleted successfully'}), 200


def get_all_proposal():
    proposals = Proposal.query.filter(
        or_(Proposal.user_proposed_to == g.user.id, Proposal.user_proposed_from == g.user.id)
    ).all()
    return jsonify({'status': 'OK', 'data': [i.serialize for i in proposals]})


def create_new_proposal():
    user_id = g.user.id
    request_id = request.json.get('request_id')

    if request_id is None:
        return jsonify({'status': 'Error', 'message': 'Missing arguments'}), 400

    req = Request.query.filter_by(id=request_id).one()

    if req.user_id == user_id:
        return jsonify({'status': 'Error', 'message': 'The maker and recipient should not be the same'}), 400

    proposal = Proposal()
    proposal.request_id = request_id
    proposal.user_proposed_to = user_id
    proposal.user_proposed_from = req.user_id
    proposal.filled = False

    db.session.add(proposal)
    db.session.commit()
    return jsonify({
        'status': 'OK',
        'message': 'New request created successfully',
        'data': proposal.serialize
    }), 201
