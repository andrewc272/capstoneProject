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

            except Exception as e:
                print("State error:", e)
                time.sleep(2)
                continue

            # ONLY send if it's the bot's turn
            if phase == "chat" and turnID == myID:
                message = self.get_message(chats)  # full chat history available

                if message:
                    try:
                        self.session.post(f"{self.url}/message", json={"message": message})
                        print(f"{self.name} sent: {message}")
                    except Exception as e:
                        print("Send error:", e)

            time.sleep(1)




