import os
import unittest

os.environ["CAPSTONE_SKIP_BOT_MANAGER"] = "1"

from app import app, reset_state  # noqa: E402
from Bot.bot import Bot

class TestUnittest(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True)
    
    def test_false(self):
        self.assertFalse(False)

class TestApp(unittest.TestCase):
    def setUp(self):
        reset_state()
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
        self.assertIn('hostId', data)
        self.assertEqual(data['botMode'], 'cloud_api')

        # Test moving to the next page
        self.app.post('/gameState', json={'nextPhase': True})
        response = self.app.get('/gameState')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('gamePhase', data)
        self.assertEqual(data['gamePhase'], 'lobby')

    def test_host_configures_local_mode(self):
        self.app.get('/addPlayer')
        payload = {"botMode": "local_ai", "localModel": "pocket", "localBotCount": 2}
        self.app.post('/gameState', json=payload)
        response = self.app.get('/gameState')
        data = response.get_json()
        self.assertEqual(data['botMode'], 'local_ai')
        self.assertEqual(data['localBotCount'], 2)

    def test_non_host_cannot_start_game(self):
        host_client = self.app
        host_client.get('/addPlayer')
        other_client = app.test_client()
        other_client.get('/addPlayer')
        resp = other_client.post('/gameState', json={'nextPhase': True})
        self.assertEqual(resp.status_code, 403)
        
