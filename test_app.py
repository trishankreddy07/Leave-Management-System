import tempfile
import os
import unittest
import app as main_app

class EmployeeLeaveSystemTest(unittest.TestCase):
    def setUp(self):
        # Create an isolated temporary SQLite database for each test run
        self.db_fd, self.db_path = tempfile.mkstemp()
        main_app.DATABASE_PATH = self.db_path
        main_app.app.config['TESTING'] = True
        main_app.app.config['SECRET_KEY'] = 'test-isolated-key-123'
        self.client = main_app.app.test_client()

        with main_app.app.app_context():
            main_app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

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
        self.assertIn('4', history_resp.get_data(as_text=True))

    def test_logout(self):
        self.client.post('/login', data={'employee_id': 101, 'password': 'Employee@123'})
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Employee Sign In', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
