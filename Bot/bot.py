import requests
import time
import os
from dotenv import load_dotenv

class Bot:
    '''This creates a bot and adds it to the game'''
    def __init__(self, name, url="http://flask-app:5000"):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({"X-Bot-Name": self.name})
        self.my_id = None
        self._responded_to_chat_len = -1  # Track which chat state we've responded to

        print(f"{self.name} connecting to {url}...")

        for attempt in range(40):
            try:
                r = self.session.get(f"{self.url}/addPlayer", timeout=3)
                if r.status_code == 200:
                    print(f"{self.name} registered with server.")
                    break
            except Exception as e:
                print(f"{self.name} waiting for Flask... {e}")
            time.sleep(2)
        else:
            print(f"{self.name} could not connect after many attempts.")
            return

        print(f"{self.name} bot initialized.")

    def get_message(self, chats=[]):
        """
        Override this in subclasses to implement actual bot behavior.
        `chats` contains the full list of (user_id, message) tuples.
        """
        time.sleep(2)
        return "Hello this is a bot"

    def _is_my_turn(self):
        """Check if it's currently this bot's turn."""
        try:
            res = self.session.get(f"{self.url}/gameState", timeout=3)
            if res.status_code == 200:
                gs = res.json()
                return (gs.get("gamePhase") == "chat" and
                        gs.get("turnID") == self.my_id)
        except Exception:
            pass
        return False

    def run(self):
        while True:
            try:
                res = self.session.get(f"{self.url}/gameState")
                if res.status_code != 200:
                    print("Could not fetch state")
                    time.sleep(1)
                    continue

                gs = res.json()
                phase = gs.get("gamePhase")
                chats = gs.get("chats", [])
                myID = gs.get("myId")
                turnID = gs.get("turnID")
                self.my_id = myID
                chat_len = len(chats)

            except Exception as e:
                print("State error:", e)
                time.sleep(2)
                continue

            # ONLY send if it's the bot's turn AND we haven't responded to this state
            if phase == "chat" and turnID == myID:
                # Already responded to this chat state? Skip.
                if chat_len <= self._responded_to_chat_len:
                    time.sleep(0.5)
                    continue

                # Double-check it's still our turn before generating
                if not self._is_my_turn():
                    time.sleep(0.5)
                    continue

                message = self.get_message(chats)

                if message:
                    # Final turn check right before sending
                    if not self._is_my_turn():
                        print(f"{self.name} skipped - turn changed during generation")
                        continue

                    try:
                        resp = self.session.post(f"{self.url}/message", json={"message": message})
                        if resp.status_code == 200:
                            print(f"{self.name} sent: {message}")
                            self._responded_to_chat_len = chat_len
                    except Exception as e:
                        print("Send error:", e)

            time.sleep(1)




