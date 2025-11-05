'''
This is the parent object of a bot and it will be used to help define every
bot and it will make it easier to spin up different instances of bots.
'''

import requests
import time
import os
from dotenv import load_dotenv

class Bot:
    def __init__(self, name, url="http://flask-app:5000"):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.get(f'{self.url}/addPlayer')  # ensures session cookie
        print(f"{self.name} connected to server.")

        # Retry connection until Flask server is ready
        for _ in range(10):  # try up to 10 times (about 30 seconds total)
            try:
                response = self.session.get(f"{self.url}/addPlayer")
                if response.status_code == 200:
                    print(f"{name} connected to Flask app successfully!")
                    break
                else:
                    print(f"Waiting for Flask app... (status {response.status_code})")
            except Exception as e:
                print("Flask not ready yet, retrying...", e)
                time.sleep(3)
        else:
            print("Failed to connect after several tries.")
            exit(1)

        print(f"{name} has been started")

    def get_message(self, chats=[]) -> str:
        time.sleep(5)
        return "Hello this is a bot"

    def run(self):
        phase = None
        chats = None
        turnID = None
        myID = None
        while True:
            # Get state
            try:
                gameState_response = self.session.get(f'{self.url}/gameState')
                if gameState_response.status_code != 200:
                    print("Error: could not fetch game state!!")
                    time.sleep(1)
                    continue

                gameState = gameState_response.json()
                phase = gameState.get("gamePhase", "")
                turnID = gameState.get("turnID")
                myID = gameState.get("myId")

                if phase == "chat":
                    chats = gameState.get("chats", [])

            except Exception as e:
                print("Error getting state:", e)
                time.sleep(2)
                continue

            if phase == "chat" and turnID == myID:
                # Get message
                message = self.get_message(chats)

                if message is not None:
                    # Post message
                    message_data = {"message": message}
                    try:
                        post_response = self.session.post(f'{self.url}/message', json=message_data)
                        print(f'Sent: {message}')
                    except Exception as e:
                        print("Error sending message:", e)
                        time.sleep(2)

            time.sleep(1)



