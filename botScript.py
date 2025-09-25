import requests
import time

# this is the web API url
url = "http://localhost:5000"

global gameState

# becasue the backend uses session cookies you need to start a session
session = requests.Session()
response = session.post(url)

while True:

    # get the gameState
    gameState_response = session.get(f'{url}/gameState')

    if gameState_response.status_code == 200:
        gameState = gameState_response.json()
        print(gameState)
    else:
        print("Error", gameState_response.txt)

    # using information from gameState to act
    if gameState.get("gamePhase") == 'lobby':
        # sign into lobby
        print(session.get(url))
        print("signed in to lobby!!")

    elif gameState.get("gamePhase") == 'chat':
        # sending a message (in the current state of the backend this can be called at anytime so be careful)
        message = {
                "message": "Hello, world! This is Werdna"
                }
        print(session.post(f'{url}/message', json=message))
    

    time.sleep(1)
