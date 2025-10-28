'''
This is the parent object of a bot and it will be used to help define every
    bot and it will make it easier to spin up different instances of bots.
'''

import requests
import time
import os
from dotenv import load_dotenv

class Bot:
    def __init__(self, name, url="http://localhost:5000"):
        self.name = name
        self.url = url
        self.session = requests.Session()
        try:
            test_response = self.session.get(f'{self.url}/addPlayer')
            if test_response.status_code != 200:
                print("Error: could not connect to session")
            else:
                print(f'{name} has been started')
        except:
            print("Error getting session started:", e)

    
    def get_message(self, chats=[]) -> str:
        time.sleep(5)
        return "Hello this is a bot"

    def run(self):
        phase = None
        chats = None
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

                if phase == "chat": chats = gameState.get("chats", [])
            
            except Exception as e:
                print("Error getting state:", e)
                time.sleep(2)
            
            if phase == "chat":
                # Get message
                message = self.get_message(chats)

                if message != None:
                    # Post message
                    message_data = {"message": message}
                    try:
                        post_response = self.session.post(f'{self.url}/message',
                                                     json=message_data)
                        print(f'Sent: {message}')
                    except Exception as e:
                        print("Error sending message:", e)
                        time.sleep(2)

            time.sleep(1)


