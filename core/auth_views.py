"""
Enhanced authentication views with concurrent login support.
"""
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import logging
import uuid
import json

logger = logging.getLogger(__name__)

class ConcurrentLoginView(LoginView):
    """
    Enhanced login view that properly handles concurrent user sessions.
    """
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Handle successful login with concurrent session support."""
        user = form.get_user()
        
        try:
            with transaction.atomic():
                # Generate unique session identifier
                session_id = str(uuid.uuid4())
                
                # Login the user (this creates a new session)
                login(self.request, user)
                
                # Store session metadata
                self.store_session_metadata(user, session_id)
                
                # Log successful concurrent login
                logger.info(f"Concurrent login successful for user {user.username} with session {session_id[:8]}")
                
                messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
                
        except Exception as e:
            logger.error(f"Error during concurrent login for user {user.username}: {e}")
            messages.error(self.request, "Login failed due to system error. Please try again.")
            return self.form_invalid(form)
        
        return redirect(self.get_success_url())
    
    def store_session_metadata(self, user, session_id):
        """Store metadata for concurrent session tracking."""
        session_key = self.request.session.session_key
        
        # Store in cache for quick access
        cache_key = f"session_meta_{session_key}"
        session_data = {
            'user_id': user.id,
            'session_id': session_id,
            'login_time': timezone.now().isoformat(),
            'user_role': getattr(user, 'userprofile', None) and user.userprofile.role,
            'last_activity': timezone.now().isoformat()
        }
        cache.set(cache_key, session_data, timeout=3600)
        
        # Track active sessions for user
        user_sessions_key = f"user_sessions_{user.id}"
        active_sessions = cache.get(user_sessions_key, [])
        active_sessions.append({
            'session_key': session_key,
            'session_id': session_id,
            'login_time': timezone.now().isoformat()
        })
        cache.set(user_sessions_key, active_sessions, timeout=3600)
    
    def get_success_url(self):
        """Redirect to appropriate dashboard based on user role."""
        return reverse_lazy('dashboard')


def get_user_active_sessions(user):
    """
    Get all active sessions for a user.
    Utility function for session management.
    """
    if not user.is_authenticated:
        return []
    
    cache_key = f"user_sessions_{user.id}"
    sessions = cache.get(cache_key, [])
    
    # Filter out expired sessions
    current_time = timezone.now()
    active_sessions = []
    
    for session_info in sessions:
        try:
            session = Session.objects.get(session_key=session_info['session_key'])
            if session.expire_date > current_time:
                active_sessions.append(session_info)
        except Session.DoesNotExist:
            continue
    
    # Update cache with filtered sessions
    cache.set(cache_key, active_sessions, timeout=3600)
    return active_sessions


def cleanup_user_sessions(user, keep_current=True, current_session_key=None):
    """
    Clean up old/expired sessions for a user.
    """
    if not user.is_authenticated:
        return 0
    
    cleaned_count = 0
    cache_key = f"user_sessions_{user.id}"
    sessions = cache.get(cache_key, [])
    
    active_sessions = []
    for session_info in sessions:
        session_key = session_info['session_key']
        
        # Keep current session if requested
        if keep_current and session_key == current_session_key:
            active_sessions.append(session_info)
            continue
        
        try:
            session = Session.objects.get(session_key=session_key)
            if session.expire_date > timezone.now():
                active_sessions.append(session_info)
            else:
                session.delete()
                cleaned_count += 1
        except Session.DoesNotExist:
            cleaned_count += 1
    
    # Update cache
    cache.set(cache_key, active_sessions, timeout=3600)
    return cleaned_count