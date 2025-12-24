"""
Middleware for handling concurrent user sessions and session management.
"""
import time
import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

class ConcurrentSessionMiddleware:
    """
    Middleware to handle concurrent user sessions properly.
    Ensures each user can have multiple active sessions without conflicts.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view
        self.process_request(request)
        
        response = self.get_response(request)
        
        # Process response after view
        self.process_response(request, response)
        
        return response

    def process_request(self, request):
        """Process incoming request for session management."""
        # Ensure user attribute exists and is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Update last activity timestamp
            cache_key = f"user_activity_{request.user.id}_{request.session.session_key}"
            cache.set(cache_key, timezone.now().timestamp(), timeout=3600)
            
            # Track concurrent sessions
            self.track_user_session(request)

    def process_response(self, request, response):
        """Process response for session cleanup."""
        # Clean up expired sessions periodically
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Only clean up occasionally to avoid performance impact
            if int(time.time()) % 100 == 0:  # Every ~100 requests
                self.cleanup_expired_sessions()
        
        return response

    def track_user_session(self, request):
        """Track active sessions for a user."""
        if not request.user.is_authenticated:
            return
            
        user_id = request.user.id
        session_key = request.session.session_key
        
        # Store active session info in cache
        cache_key = f"active_sessions_{user_id}"
        active_sessions = cache.get(cache_key, set())
        active_sessions.add(session_key)
        cache.set(cache_key, active_sessions, timeout=3600)

    def cleanup_expired_sessions(self):
        """Clean up expired sessions from database."""
        try:
            expired_sessions = Session.objects.filter(
                expire_date__lt=timezone.now()
            )
            count = expired_sessions.count()
            if count > 0:
                expired_sessions.delete()
                logger.info(f"Cleaned up {count} expired sessions")
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")


@login_required
@require_http_methods(["GET"])
def get_active_sessions_api(request):
    """API endpoint to get user's active sessions."""
    from .auth_views import get_user_active_sessions
    try:
        sessions = get_user_active_sessions(request.user)
        session_data = []
        
        for session_info in sessions:
            session_data.append({
                'session_id': session_info.get('session_id', 'Unknown')[:8],
                'login_time': session_info.get('login_time', 'Unknown'),
                'is_current': session_info.get('session_key') == request.session.session_key
            })
        
        return JsonResponse({
            'success': True,
            'sessions': session_data,
            'total_sessions': len(session_data)
        })
    except Exception as e:
        logger.error(f"Error fetching active sessions for user {request.user.username}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch session data'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def terminate_session_api(request):
    """API endpoint to terminate a specific session."""
    try:
        data = json.loads(request.body)
        session_key = data.get('session_key')
        
        if not session_key:
            return JsonResponse({
                'success': False,
                'error': 'Session key required'
            }, status=400)
        
        # Don't allow terminating current session via API
        if session_key == request.session.session_key:
            return JsonResponse({
                'success': False,
                'error': 'Cannot terminate current session'
            }, status=400)
        
        # Terminate the session
        try:
            session = Session.objects.get(session_key=session_key)
            session.delete()
            
            # Update cache
            user_sessions_key = f"user_sessions_{request.user.id}"
            active_sessions = cache.get(user_sessions_key, [])
            active_sessions = [s for s in active_sessions if s.get('session_key') != session_key]
            cache.set(user_sessions_key, active_sessions, timeout=3600)
            
            logger.info(f"Session {session_key[:8]} terminated by user {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Session terminated successfully'
            })
            
        except Session.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session not found or already expired'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to terminate session'
        }, status=500)


class SessionSecurityMiddleware:
    """
    Enhanced session security middleware for concurrent access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add session security headers
        response = self.get_response(request)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Add security headers
            response['X-Session-ID'] = request.session.session_key[:8]  # Partial for debugging
            try:
                user_role = request.user.userprofile.role if hasattr(request.user, 'userprofile') else 'unknown'
            except:
                user_role = 'unknown'
            response['X-User-Role'] = user_role
        
        return response