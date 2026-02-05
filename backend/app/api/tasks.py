"""
Tasks API - Endpoints for triggering background tasks
Supports both manual triggering and Cloudflare Cron Triggers
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime

from app.utils import jwt_required_custom, get_current_user, admin_required, APIResponse
from app.services.task_service import (
    TaskService, 
    auto_escalate_task, 
    send_reminders_task,
    cleanup_notifications_task,
    calculate_stats_task
)

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/run-escalation', methods=['POST'])
@jwt_required_custom
@admin_required
def run_escalation():
    """
    Manually trigger auto-escalation of old complaints.
    Admin only.
    """
    try:
        # Run synchronously for immediate feedback
        result = TaskService.auto_escalate_complaints()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Auto-escalation completed. {result.get('escalated', 0)} complaints escalated.",
                'data': result
            }), 200
        else:
            return APIResponse.error(result.get('error', 'Task failed'), 500)
            
    except Exception as e:
        current_app.logger.error(f'Escalation task error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/run-reminders', methods=['POST'])
@jwt_required_custom
@admin_required
def run_reminders():
    """
    Manually trigger reminder notifications.
    Admin only.
    """
    try:
        result = TaskService.send_pending_reminders()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Reminders sent. {result.get('reminders_sent', 0)} reminders sent.",
                'data': result
            }), 200
        else:
            return APIResponse.error(result.get('error', 'Task failed'), 500)
            
    except Exception as e:
        current_app.logger.error(f'Reminder task error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/run-cleanup', methods=['POST'])
@jwt_required_custom
@admin_required
def run_cleanup():
    """
    Manually trigger notification cleanup.
    Admin only.
    """
    try:
        days = request.args.get('days', 30, type=int)
        result = TaskService.cleanup_old_notifications(days)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Cleanup completed. {result.get('deleted', 0)} old notifications deleted.",
                'data': result
            }), 200
        else:
            return APIResponse.error(result.get('error', 'Task failed'), 500)
            
    except Exception as e:
        current_app.logger.error(f'Cleanup task error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/calculate-stats', methods=['POST'])
@jwt_required_custom
def calculate_stats():
    """
    Trigger stats calculation for user's society.
    """
    user = get_current_user()
    
    try:
        result = TaskService.calculate_society_stats(user.society_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Statistics calculated successfully',
                'data': result['stats']
            }), 200
        else:
            return APIResponse.error(result.get('error', 'Task failed'), 500)
            
    except Exception as e:
        current_app.logger.error(f'Stats calculation error: {e}')
        return APIResponse.error(str(e), 500)


# ============================================
# Cloudflare Cron Trigger Endpoints
# These can be called by Cloudflare Workers Cron Triggers
# ============================================

@tasks_bp.route('/cron/escalate', methods=['POST'])
def cron_escalate():
    """
    Cloudflare Cron Trigger endpoint for auto-escalation.
    Secured via secret header.
    """
    # Verify cron secret
    cron_secret = request.headers.get('X-Cron-Secret')
    expected_secret = current_app.config.get('CRON_SECRET', 'default-cron-secret')
    
    if cron_secret != expected_secret:
        return APIResponse.error('Unauthorized', 401)
    
    try:
        result = TaskService.auto_escalate_complaints()
        return jsonify({
            'success': True,
            'task': 'auto_escalate',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f'Cron escalate error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/cron/reminders', methods=['POST'])
def cron_reminders():
    """
    Cloudflare Cron Trigger endpoint for reminders.
    Secured via secret header.
    """
    cron_secret = request.headers.get('X-Cron-Secret')
    expected_secret = current_app.config.get('CRON_SECRET', 'default-cron-secret')
    
    if cron_secret != expected_secret:
        return APIResponse.error('Unauthorized', 401)
    
    try:
        result = TaskService.send_pending_reminders()
        return jsonify({
            'success': True,
            'task': 'send_reminders',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f'Cron reminders error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/cron/cleanup', methods=['POST'])
def cron_cleanup():
    """
    Cloudflare Cron Trigger endpoint for cleanup.
    Secured via secret header.
    """
    cron_secret = request.headers.get('X-Cron-Secret')
    expected_secret = current_app.config.get('CRON_SECRET', 'default-cron-secret')
    
    if cron_secret != expected_secret:
        return APIResponse.error('Unauthorized', 401)
    
    try:
        result = TaskService.cleanup_old_notifications(days=30)
        return jsonify({
            'success': True,
            'task': 'cleanup_notifications',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        current_app.logger.error(f'Cron cleanup error: {e}')
        return APIResponse.error(str(e), 500)


@tasks_bp.route('/status', methods=['GET'])
@jwt_required_custom
@admin_required
def task_status():
    """
    Get task system status.
    Admin only.
    """
    import os
    
    celery_enabled = os.environ.get('CELERY_ENABLED', 'false').lower() == 'true'
    serverless = os.environ.get('SERVERLESS', 'false').lower() == 'true'
    
    return jsonify({
        'success': True,
        'data': {
            'celery_enabled': celery_enabled,
            'serverless_mode': serverless,
            'task_mode': 'celery' if celery_enabled else ('sync' if serverless else 'threaded'),
            'available_tasks': [
                {'name': 'auto_escalate', 'description': 'Auto-escalate old complaints (7+ days)'},
                {'name': 'send_reminders', 'description': 'Send reminders for stale complaints (3+ days)'},
                {'name': 'cleanup_notifications', 'description': 'Delete old read notifications'},
                {'name': 'calculate_stats', 'description': 'Calculate society statistics'}
            ],
            'cron_endpoints': [
                {'path': '/api/tasks/cron/escalate', 'schedule': 'Daily at midnight'},
                {'path': '/api/tasks/cron/reminders', 'schedule': 'Daily at 9 AM'},
                {'path': '/api/tasks/cron/cleanup', 'schedule': 'Weekly on Sunday'}
            ]
        }
    }), 200
