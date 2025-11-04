import unittest
from app import app
from Bot.bot import Bot

class TestUnittest(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True)
    
    def test_false(self):
        self.assertFalse(False)

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html', response.data)

    def test_gameState(self):
        
        # Test initial state
        response = self.app.get('/gameState')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('gamePhase', data)
        self.assertEqual(data['gamePhase'], 'intro')

        # Test moving to the next page
        self.app.post('/gameState', json={'nextPhase': True})
        response = self.app.get('/gameState')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('gamePhase', data)
        self.assertEqual(data['gamePhase'], 'lobby')
        
