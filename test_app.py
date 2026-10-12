import unittest
from app import app, init_db

class EmployeeLeaveSystemTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-321'
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_unauthenticated_access_redirects(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_login_page_renders_clean_html(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Employee Sign In', html)
        self.assertNotIn('{{', html)
        self.assertNotIn('{%', html)

    def test_invalid_login_credentials(self):
        response = self.client.post('/login', data={'employee_id': 101, 'password': 'wrong-password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid Employee ID or password', response.get_data(as_text=True))

    def test_valid_login_and_dashboard_render(self):
        response = self.client.post('/login', data={'employee_id': 101, 'password': 'Employee@123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Welcome back, Trishank Reddy', html)
        self.assertIn('Total Leave Allowance', html)
        self.assertNotIn('{{', html)

    def test_apply_leave_flow_and_history(self):
        self.client.post('/login', data={'employee_id': 103, 'password': 'Employee@123'})
        response = self.client.post('/apply-leave', data={'leave_type': 1, 'days': 4}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Leave applied successfully', html)
        self.assertIn('16 Days Remaining', html)

        # Check history table
        history_resp = self.client.get('/history')
        self.assertEqual(history_resp.status_code, 200)
        self.assertIn('Casual', history_resp.get_data(as_text=True))

    def test_logout(self):
        self.client.post('/login', data={'employee_id': 101, 'password': 'Employee@123'})
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Employee Sign In', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
