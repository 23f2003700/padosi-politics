"""
Karma API - Karma score management and leaderboards
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import User, Society, KarmaLog
from app.utils import (
    jwt_required_custom, get_current_user,
    APIResponse, paginate_query, get_pagination_params
)

karma_bp = Blueprint('karma', __name__)


@karma_bp.route('/users/<int:user_id>/karma', methods=['GET'])
@jwt_required_custom
def get_user_karma(user_id):
    """Get karma score and history for a user."""
    current_user = get_current_user()
    user = User.query.get_or_404(user_id)
    
    # Users can only see karma of users in same society
    if user.society_id != current_user.society_id and not current_user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    # Get karma history
    page, per_page = get_pagination_params()
    
    query = KarmaLog.query.filter_by(user_id=user_id)\
        .order_by(KarmaLog.created_at.desc())
    
    pagination = paginate_query(query, page, per_page)
    
    # Calculate monthly karma
    from datetime import datetime
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    monthly_karma = KarmaLog.calculate_monthly_karma(user_id, current_year, current_month)
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'total_karma': user.karma_score,
            'monthly_karma': monthly_karma,
            'history': [log.to_dict() for log in pagination['items']],
            'pagination': {
                'total': pagination['total'],
                'pages': pagination['pages'],
                'page': pagination['page'],
                'per_page': pagination['per_page']
            }
        }
    }), 200


@karma_bp.route('/my-karma', methods=['GET'])
@jwt_required_custom
def get_my_karma():
    """Get current user's karma score and history."""
    user = get_current_user()
    return get_user_karma(user.id)


@karma_bp.route('/society/<int:society_id>/karma-leaderboard', methods=['GET'])
@jwt_required_custom
def get_karma_leaderboard(society_id):
    """Get karma leaderboard for a society."""
    current_user = get_current_user()
    society = Society.query.get_or_404(society_id)
    
    # Verify access
    if society.id != current_user.society_id and not current_user.is_admin():
        return APIResponse.error('Access denied', 403)
    
    # Get parameters
    limit = request.args.get('limit', 10, type=int)
    leaderboard_type = request.args.get('type', 'top')  # 'top' or 'bottom'
    
    # Limit max results
    limit = min(limit, 50)
    
    # Get leaderboard
    if leaderboard_type == 'bottom':
        order = 'asc'
    else:
        order = 'desc'
    
    leaders = society.get_leaderboard(limit=limit, order=order)
    
    return jsonify({
        'success': True,
        'data': {
            'society_id': society_id,
            'society_name': society.name,
            'average_karma': society.average_karma,
            'type': leaderboard_type,
            'leaderboard': [
                {
                    'rank': idx + 1,
                    'user_id': user.id,
                    'full_name': user.full_name,
                    'flat_number': user.flat_number,
                    'wing': user.wing,
                    'karma_score': user.karma_score,
                    'avatar_url': user.avatar_url
                }
                for idx, user in enumerate(leaders)
            ]
        }
    }), 200


@karma_bp.route('/leaderboard', methods=['GET'])
@jwt_required_custom
def get_my_society_leaderboard():
    """Get karma leaderboard for current user's society."""
    user = get_current_user()
    return get_karma_leaderboard(user.society_id)


@karma_bp.route('/karma-stats', methods=['GET'])
@jwt_required_custom
def get_karma_stats():
    """Get karma statistics for current user."""
    user = get_current_user()
    
    # Get karma breakdown by reason
    from sqlalchemy import func
    
    breakdown = db.session.query(
        KarmaLog.reason,
        func.sum(KarmaLog.points).label('total_points'),
        func.count(KarmaLog.id).label('count')
    ).filter(KarmaLog.user_id == user.id)\
     .group_by(KarmaLog.reason).all()
    
    # Get rank in society
    higher_karma_count = User.query.filter(
        User.society_id == user.society_id,
        User.karma_score > user.karma_score,
        User.active == True
    ).count()
    
    rank = higher_karma_count + 1
    total_users = User.query.filter(
        User.society_id == user.society_id,
        User.active == True
    ).count()
    
    return jsonify({
        'success': True,
        'data': {
            'total_karma': user.karma_score,
            'rank': rank,
            'total_users': total_users,
            'percentile': round((total_users - rank + 1) / total_users * 100, 1) if total_users > 0 else 100,
            'breakdown': [
                {
                    'reason': r.reason,
                    'total_points': r.total_points,
                    'count': r.count
                }
                for r in breakdown
            ]
        }
    }), 200
