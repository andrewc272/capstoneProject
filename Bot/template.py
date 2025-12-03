import requests
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

#Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


url = "http://localhost:5000"
session = requests.Session()
session.headers.update({"X-Bot-Name": os.getenv("BOT_NAME", "TemplateBot")})

#initializes the state
seen_messages = set()

#starts a session
session.post(url)

while True:
    try:
        gameState_response = session.get(f'{url}/gameState')
        if gameState_response.status_code != 200:
            print("Error: Could not fetch game state :(")
            time.sleep(1)
            continue

        gameState = gameState_response.json()
        chats = gameState.get("chats", [])
        phase = gameState.get("gamePhase", "")

        #ONLY in chat phase
        if phase == "chat":
            for msg in chats:
                sender = msg[0] if len(msg) > 0 else None
                text = msg[1].strip() if len(msg) > 1 else ""
                msg_id = (sender, text)

                #Skip messages that've already been read
                if msg_id in seen_messages:
                    continue
                seen_messages.add(msg_id)

                #Checks if the message is calling the bot
                if text.lower().startswith("@bot"):
                    print(f"Detected bot summon: {text}")

                    if text.lower().startswith("@bot"):
                        prompt = text[len("@bot"):].strip()
                    else:
                        prompt = text.strip()
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are playing a game. You are playing against a human, who is trying to detect if you are a bot. You must deceive them into thinking you are human. You are supposed to ask each other questions to figure out if each other is the bot. Keep responses, short, skeptical, and not over excited. You must put yourself in the shoes of the human playing and try to behave as they would. You have to also question the user to show you are trying to figure out if they are a bot. Also, the game is turn-based and you will likely be first. You must send the first message. Once the game starts, send a cautious message just to test the waters."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    bot_reply = response.choices[0].message.content.strip()

                    #Sends message back to Flask
                    message_data = {"message": bot_reply}
                    post_response = session.post(f"{url}/message", json=message_data)
                    print("Bot replied:", bot_reply)
                    print("POST result:", post_response.status_code)

        time.sleep(1)

    except Exception as e:
        print("Error in bot loop:", e)
        time.sleep(2)
