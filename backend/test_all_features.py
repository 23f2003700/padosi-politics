"""
Comprehensive Feature Test Script for Padosi Politics
Tests all features including API endpoints, database, email, and more.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Test credentials
TEST_USERS = {
    'admin': {'email': 'admin@padosipolitics.com', 'password': 'password123'},
    'secretary': {'email': 'secretary@greenvalley.com', 'password': 'password123'},
    'resident': {'email': 'resident1@greenvalley.com', 'password': 'password123'}
}

class FeatureTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.created_complaint_id = None
        
    def log(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"       {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        return success
    
    def login(self, role):
        """Login and store token for a role."""
        user = TEST_USERS[role]
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=user,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                self.tokens[role] = data['data']['access_token']
                return True
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def get_headers(self, role):
        """Get authorization headers for a role."""
        return {
            'Authorization': f'Bearer {self.tokens.get(role, "")}',
            'Content-Type': 'application/json'
        }
    
    def test_health_check(self):
        """Test if the server is running."""
        try:
            response = requests.get("http://localhost:5000/api/auth/me", headers=self.get_headers('resident') if 'resident' in self.tokens else {})
            # If no token yet, just check server responds
            if not self.tokens:
                response = requests.post(f"{BASE_URL}/auth/login", json=TEST_USERS['resident'], headers={'Content-Type': 'application/json'})
            return self.log("Health Check", response.status_code in [200, 401], f"Server responding")
        except Exception as e:
            return self.log("Health Check", False, str(e))
    
    def test_authentication(self):
        """Test authentication for all user types."""
        print("\n🔐 Testing Authentication...")
        
        for role in TEST_USERS:
            success = self.login(role)
            self.log(f"Login as {role}", success)
        
        # Test invalid login
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={'email': 'invalid@test.com', 'password': 'wrong'},
            headers={'Content-Type': 'application/json'}
        )
        self.log("Invalid login rejected", response.status_code == 401)
    
    def test_user_profile(self):
        """Test user profile endpoints."""
        print("\n👤 Testing User Profile...")
        
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=self.get_headers('resident')
        )
        self.log("Get current user", response.status_code == 200)
        
        if response.status_code == 200:
            user = response.json()['data']
            self.log("User has email", 'email' in user)
            self.log("User has karma", 'karma_score' in user or 'karma_points' in user)
    
    def test_dashboard(self):
        """Test dashboard statistics."""
        print("\n📊 Testing Dashboard...")
        
        response = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers=self.get_headers('resident')
        )
        self.log("Get dashboard stats", response.status_code == 200)
        
        if response.status_code == 200:
            data = response.json()['data']
            self.log("Has my_complaints_count", 'my_complaints_count' in data)
            self.log("Has my_karma", 'my_karma' in data)
    
    def test_create_complaint(self):
        """Test creating a new complaint."""
        print("\n📝 Testing Complaint Creation...")
        
        complaint_data = {
            'title': f'Test Complaint - {datetime.now().strftime("%H:%M:%S")}',
            'description': 'This is a test complaint created by the automated testing script. It contains enough characters to pass validation.',
            'category': 'maintenance',
            'priority': 'medium',
            'is_anonymous': False
        }
        
        response = requests.post(
            f"{BASE_URL}/complaints",
            json=complaint_data,
            headers=self.get_headers('resident')
        )
        
        success = response.status_code in [200, 201]
        self.log("Create complaint", success, f"Status: {response.status_code}")
        
        if success:
            self.created_complaint_id = response.json()['data']['id']
            self.log("Complaint ID received", self.created_complaint_id is not None)
    
    def test_list_complaints(self):
        """Test listing complaints."""
        print("\n📋 Testing Complaint Listing...")
        
        response = requests.get(
            f"{BASE_URL}/complaints",
            headers=self.get_headers('resident')
        )
        self.log("List all complaints", response.status_code == 200)
        
        if response.status_code == 200:
            data = response.json()['data']
            # Handle both list and dict formats
            if isinstance(data, list):
                complaints = data
            else:
                complaints = data.get('complaints', data.get('items', []))
            self.log("Complaints returned", len(complaints) > 0, f"Count: {len(complaints)}")
        
        # Test with filters
        response = requests.get(
            f"{BASE_URL}/complaints?status=open&category=maintenance",
            headers=self.get_headers('resident')
        )
        self.log("List with filters", response.status_code == 200)
    
    def test_complaint_details(self):
        """Test getting complaint details."""
        print("\n🔍 Testing Complaint Details...")
        
        if not self.created_complaint_id:
            # Try to get first complaint
            response = requests.get(
                f"{BASE_URL}/complaints",
                headers=self.get_headers('resident')
            )
            if response.status_code == 200:
                data = response.json()['data']
                complaints = data if isinstance(data, list) else data.get('complaints', data.get('items', []))
                if complaints:
                    self.created_complaint_id = complaints[0]['id']
        
        if self.created_complaint_id:
            response = requests.get(
                f"{BASE_URL}/complaints/{self.created_complaint_id}",
                headers=self.get_headers('resident')
            )
            self.log("Get complaint details", response.status_code == 200)
            
            if response.status_code == 200:
                complaint = response.json()['data']
                self.log("Has title", 'title' in complaint)
                self.log("Has status", 'status' in complaint)
                self.log("Has category", 'category' in complaint)
    
    def test_vote_on_complaint(self):
        """Test voting on complaints."""
        print("\n👍 Testing Voting System...")
        
        if self.created_complaint_id:
            response = requests.post(
                f"{BASE_URL}/complaints/{self.created_complaint_id}/vote",
                headers=self.get_headers('resident')
            )
            self.log("Vote on complaint", response.status_code in [200, 201, 400])  # 400 if already voted
    
    def test_comment_on_complaint(self):
        """Test commenting on complaints."""
        print("\n💬 Testing Comments...")
        
        if self.created_complaint_id:
            comment_data = {
                'comment_text': 'This is a test comment from the automated testing script.'
            }
            response = requests.post(
                f"{BASE_URL}/complaints/{self.created_complaint_id}/comments",
                json=comment_data,
                headers=self.get_headers('resident')
            )
            self.log("Add comment", response.status_code in [200, 201], f"Status: {response.status_code}")
            
            # Get comments
            response = requests.get(
                f"{BASE_URL}/complaints/{self.created_complaint_id}/comments",
                headers=self.get_headers('resident')
            )
            self.log("Get comments", response.status_code == 200)
    
    def test_status_update(self):
        """Test updating complaint status (as secretary)."""
        print("\n🔄 Testing Status Updates...")
        
        if self.created_complaint_id:
            update_data = {
                'status': 'acknowledged',
                'resolution_note': 'Complaint acknowledged by testing script'
            }
            response = requests.patch(
                f"{BASE_URL}/complaints/{self.created_complaint_id}/status",
                json=update_data,
                headers=self.get_headers('secretary')
            )
            self.log("Update status (secretary)", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_escalation(self):
        """Test escalation functionality."""
        print("\n⬆️ Testing Escalation...")
        
        if self.created_complaint_id:
            escalation_data = {
                'reason': 'Testing escalation functionality'
            }
            response = requests.post(
                f"{BASE_URL}/escalations/complaints/{self.created_complaint_id}/escalate",
                json=escalation_data,
                headers=self.get_headers('secretary')
            )
            self.log("Escalate complaint", response.status_code in [200, 201, 400], f"Status: {response.status_code}")
    
    def test_notifications(self):
        """Test notifications system."""
        print("\n🔔 Testing Notifications...")
        
        response = requests.get(
            f"{BASE_URL}/notifications",
            headers=self.get_headers('resident')
        )
        self.log("Get notifications", response.status_code == 200)
        
        response = requests.get(
            f"{BASE_URL}/notifications/unread-count",
            headers=self.get_headers('resident')
        )
        self.log("Get unread count", response.status_code == 200)
    
    def test_leaderboard(self):
        """Test leaderboard/karma system."""
        print("\n🏆 Testing Leaderboard...")
        
        response = requests.get(
            f"{BASE_URL}/leaderboard",
            headers=self.get_headers('resident')
        )
        self.log("Get leaderboard", response.status_code == 200, f"Status: {response.status_code}")
        
        response = requests.get(
            f"{BASE_URL}/my-karma",
            headers=self.get_headers('resident')
        )
        self.log("Get my karma", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_admin_features(self):
        """Test admin-specific features."""
        print("\n👑 Testing Admin Features...")
        
        # Dashboard stats (admin)
        response = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers=self.get_headers('admin')
        )
        self.log("Get admin dashboard stats", response.status_code == 200, f"Status: {response.status_code}")
        
        # Society stats (admin)
        response = requests.get(
            f"{BASE_URL}/dashboard/society-stats",
            headers=self.get_headers('admin')
        )
        self.log("Get society stats (admin)", response.status_code == 200, f"Status: {response.status_code}")
        
        # Get karma stats (admin)
        response = requests.get(
            f"{BASE_URL}/karma-stats",
            headers=self.get_headers('admin')
        )
        self.log("Admin karma stats", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_society_features(self):
        """Test society-related features."""
        print("\n🏘️ Testing Society Features...")
        
        # First get the society ID from the secretary's profile
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=self.get_headers('secretary')
        )
        if response.status_code == 200:
            data = response.json()
            society_id = data.get('society_id', 1)
        else:
            society_id = 1
        
        response = requests.get(
            f"{BASE_URL}/societies/{society_id}/stats",
            headers=self.get_headers('secretary')
        )
        self.log("Get society stats", response.status_code == 200, f"Status: {response.status_code}")
        
        response = requests.get(
            f"{BASE_URL}/societies/{society_id}/residents",
            headers=self.get_headers('secretary')
        )
        self.log("Get society residents", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_my_complaints(self):
        """Test user's own complaints."""
        print("\n📑 Testing My Complaints...")
        
        response = requests.get(
            f"{BASE_URL}/complaints",
            headers=self.get_headers('resident'),
            params={'my_complaints': 'true'}
        )
        self.log("Get my complaints", response.status_code == 200, f"Status: {response.status_code}")
    
    def test_email_service(self):
        """Test email service (without actually sending)."""
        print("\n📧 Testing Email Service...")
        
        try:
            # Import and test email templates exist
            from app.services.email_service import TEMPLATES, send_email
            self.log("Email service imported", True)
            self.log("Email templates loaded", len(TEMPLATES) > 0, f"Templates: {list(TEMPLATES.keys())}")
        except ImportError as e:
            self.log("Email service import", False, str(e))
    
    def test_celery_tasks(self):
        """Test Celery tasks are defined (without running)."""
        print("\n⚙️ Testing Celery Configuration...")
        
        try:
            from app.celery_app import celery
            from app.tasks.scheduled import auto_escalate_old_complaints, send_reminder_notifications
            self.log("Celery app configured", True)
            self.log("Scheduled tasks defined", True)
        except ImportError as e:
            self.log("Celery configuration", False, str(e))
    
    def print_summary(self):
        """Print test summary."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print("="*60)
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.test_results:
                if not r['success']:
                    print(f"  - {r['test']}: {r['message']}")
        
        return failed == 0


def run_tests():
    """Run all feature tests."""
    print("="*60)
    print("🧪 PADOSI POLITICS - COMPREHENSIVE FEATURE TEST")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("="*60)
    
    tester = FeatureTester()
    
    # Run all tests
    tester.test_health_check()
    tester.test_authentication()
    tester.test_user_profile()
    tester.test_dashboard()
    tester.test_create_complaint()
    tester.test_list_complaints()
    tester.test_complaint_details()
    tester.test_vote_on_complaint()
    tester.test_comment_on_complaint()
    tester.test_status_update()
    tester.test_escalation()
    tester.test_notifications()
    tester.test_leaderboard()
    tester.test_admin_features()
    tester.test_society_features()
    tester.test_my_complaints()
    
    # Return summary
    success = tester.print_summary()
    return success


if __name__ == '__main__':
    import sys
    
    # Add parent directory to path for imports
    sys.path.insert(0, '.')
    
    success = run_tests()
    sys.exit(0 if success else 1)
