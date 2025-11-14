import requests
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
from bot import Bot

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class openAI(Bot):
    def __init__(self, name, url="http://flask-app:5000"):
        super().__init__(name, url)
        self.seen_messages = set()

    def get_message(self, chats=None):
        if chats is None or not chats:
            chats = [("host", "Hello, you are starting the game. Try to convince others you are not a bot or make an accusation.")]

        messages_for_openai = [
            {"role": "system", "content": (
                "You are playing a game. You are playing against a human, who is trying to detect if you are a bot. "
                "You must deceive them into thinking they are human. You are supposed to ask each other questions to figure out "
                "if each other is the bot. Keep responses short, skeptical, and not over excited. "
                "You must put yourself in the shoes of the human playing and behave naturally. "
                "The game is turn-based. Send the first message if it is your turn. Make grammatical, punctuation, "
                "spelling, and capitalization mistakes like humans. Shorten responses to reduce information for others."
            )}
        ]

        for sender, text in chats:
            msg_id = (sender, text.strip())
            if msg_id not in self.seen_messages:
                self.seen_messages.add(msg_id)
                role = "assistant" if sender == self.name else "user"
                messages_for_openai.append({"role": role, "content": text.strip()})

        if len(messages_for_openai) == 1:
            messages_for_openai.append({"role": "user", "content": "I'm thinking..."})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_openai
        )

        return response.choices[0].message.content.strip()


if __name__ == '__main__':
    bot_name = os.getenv("BOT_NAME")
    bot = openAI(bot_name, "http://flask-app:5000")
    bot.run()



