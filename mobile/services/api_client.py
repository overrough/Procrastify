"""
API Client for Procrastify Mobile App
Handles all communication with Flask backend
"""
import requests
from functools import wraps


class APIClient:
    """HTTP Client for Procrastify API"""
    
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.token = None
        self.timeout = 10
    
    def set_token(self, token):
        """Set authentication token"""
        self.token = token
    
    def _get_headers(self):
        """Get request headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response):
        """Handle API response"""
        try:
            data = response.json()
        except:
            data = {"error": "Invalid response from server"}
        
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "data": data
        }
    
    def _request(self, method, endpoint, data=None):
        """Make an API request"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                return {"success": False, "error": "Invalid method"}
            
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to server. Make sure the backend is running."}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============= AUTH ENDPOINTS =============
    
    def register(self, email, password, name):
        """Register a new user"""
        return self._request("POST", "/auth/register", {
            "email": email,
            "password": password,
            "name": name
        })
    
    def login(self, email, password):
        """Login user"""
        return self._request("POST", "/auth/login", {
            "email": email,
            "password": password
        })
    
    def get_profile(self):
        """Get current user profile"""
        return self._request("GET", "/auth/profile")
    
    def verify_token(self):
        """Verify if token is valid"""
        return self._request("GET", "/auth/verify")
    
    # ============= TASK ENDPOINTS =============
    
    def get_tasks(self, status="pending"):
        """Get all tasks"""
        return self._request("GET", f"/tasks?status={status}")
    
    def create_task(self, title, deadline, complexity, category="Study", description=""):
        """Create a new task"""
        return self._request("POST", "/tasks", {
            "title": title,
            "deadline": deadline,
            "complexity": complexity,
            "category": category,
            "description": description
        })
    
    def update_task(self, task_id, **kwargs):
        """Update a task"""
        return self._request("PUT", f"/tasks/{task_id}", kwargs)
    
    def complete_task(self, task_id):
        """Mark task as complete"""
        return self._request("PATCH", f"/tasks/{task_id}/complete")
    
    def delete_task(self, task_id):
        """Delete a task"""
        return self._request("DELETE", f"/tasks/{task_id}")
    
    # ============= ANALYTICS ENDPOINTS =============
    
    def get_daily_analytics(self):
        """Get today's analytics"""
        return self._request("GET", "/analytics/daily")
    
    def get_weekly_analytics(self):
        """Get weekly analytics"""
        return self._request("GET", "/analytics/weekly")
    
    def log_app_usage(self, app_name, duration_seconds, session_id=None):
        """Log app usage"""
        return self._request("POST", "/analytics/app-usage", {
            "app_name": app_name,
            "duration_seconds": duration_seconds,
            "session_id": session_id
        })
    
    def check_distraction(self, app_name, time_on_app, session_id=None):
        """Check if app is a distraction"""
        return self._request("POST", "/analytics/check-distraction", {
            "app_name": app_name,
            "time_on_app": time_on_app,
            "session_id": session_id
        })
    
    def get_focus_score(self):
        """Get current focus score"""
        return self._request("GET", "/analytics/focus-score")
    
    # ============= SESSION ENDPOINTS =============
    
    def start_session(self, task_id=None, duration=25):
        """Start a focus session"""
        return self._request("POST", "/sessions/start", {
            "task_id": task_id,
            "duration": duration
        })
    
    def end_session(self, session_id, completed=False, interruptions=0, focus_score=0):
        """End a focus session"""
        return self._request("POST", "/sessions/end", {
            "session_id": session_id,
            "completed": completed,
            "interruptions": interruptions,
            "focus_score": focus_score
        })
    
    def get_session_history(self, limit=10):
        """Get session history"""
        return self._request("GET", f"/sessions/history?limit={limit}")
    
    def get_streak(self):
        """Get current streak"""
        return self._request("GET", "/sessions/streak")
    
    def get_session_stats(self):
        """Get overall session statistics"""
        return self._request("GET", "/sessions/stats")
