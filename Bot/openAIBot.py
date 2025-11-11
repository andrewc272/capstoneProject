import requests
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
from bot import Bot

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
seen_messages = set()

class openAI(Bot):
    def get_message(self, chat = [("host","Hello, you are starting the game try to convince others you are not a bot or make an accusation.")]):
        if chat == []: chat = [("host","Hello, you are starting the game try to convice others you are not a bot or make an accusation.")]
        for msg in chat:
            sender = msg[0] if len(msg) > 0 else None
            text = msg[1].strip() if len(msg) > 1 else ""
            msg_id = (sender, text)

            if msg_id in seen_messages:
                continue
            seen_messages.add(msg_id)

            print(f'Detected bot summon: {text}')
            if text.lower().startswith("@bot"):
                prompt = text[len("@bot"):].strip()
            else:
                prompt = text.strip()
            response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are playing a game. You are playing against a human, who is trying to detect if you are a bot. You must deceive them into thinking they are human. You are supposed to ask each other questions to figure out if each other is the bot. Keep responses, short, skeptical, and not over excited. You must put yourself in the shoes of the human playing and try to behave as they would. You have to also question the user to show you are trying to figure out if they are a bot. Also, the game is turn-based, and you will likely be first. Send the first message, don't wait for somebody else to send one. Make a LOT of grammatical, puncual, spelling and capitalization mistakes much like humans would in a chat room. Shorten responses to decrease the amount of information the human players have to go off of."},
                        {"role": "user", "content": prompt}
                        ]
                    )
            return response.choices[0].message.content.strip()


if __name__ == '__main__':
    bot = openAI("bot", "http://localhost:5000") # add "http://localhost:5000" to run without docker (for dev)
    bot.run()
