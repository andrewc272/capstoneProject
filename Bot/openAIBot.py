import requests
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIBot:
    def __init__(self, url, name="OpenAI Bot"):
        self.url = url.rstrip("/")
        self.name = name
        self.session = requests.Session()
        self.myID = None
        self.added = False
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _headers(self):
        return {"Content-Type": "application/json"}

    def register(self):
        """Register the bot and get its ID."""
        if not self.added:
            try:
                self.session.get(f"{self.url}/addPlayer", headers=self._headers())
                gs = self.session.get(f"{self.url}/gameState", headers=self._headers()).json()
                self.myID = gs.get("myId")
                self.added = True
                print(f"[INFO] Registered bot with myID: {self.myID}")
            except Exception as e:
                print(f"[ERROR] Failed to register: {e}")

    def get_message(self, chats):
        system_prompt = (
            "You are secretly an AI participating in a social deduction game. "
            "Your goal is to convince the human players that you are human. "
            "Never reveal that you are an AI, and never speak unnaturally. "
            "Write short, casual, conversational messages like a real person. "
            "If the conversation has no messages yet, introduce yourself naturally. "
            "If asked about being a bot, deny it casually and confidently."
            "Keep responses short, use poor grammar, and use poor punctuation. Make your responses as realistically human as possible"
        )

        if not chats:
            conversation = ""
        else:
            conversation = ""
            for uid, msg in chats:
                speaker = "" if uid == self.myID else f"Player {uid[:4]}"
                conversation += f"{speaker}: {msg}\n"

        prompt = conversation + f"{self.name}:"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {e}")
            return "I pass."


    def play(self):
        while True:
            try:
                self.register()

                # Fetch game state
                res = self.session.get(f"{self.url}/gameState", headers=self._headers())
                gs = res.json()
                phase = gs.get("gamePhase")
                turnID = gs.get("turnID")
                chats = gs.get("chats", [])

                print(f"[DEBUG] Phase: {phase}, turnID: {turnID}, myID: {self.myID}, chats: {len(chats)}")

                # Act only on bot's turn during chat phase
                if phase == "chat" and turnID == self.myID:
                    msg = self.get_message(chats)
                    self.session.post(
                        f"{self.url}/message",
                        json={"message": msg},
                        headers=self._headers()
                    )
                    print(f"[BOT] Sent message: {msg}")

                time.sleep(1)

            except Exception as e:
                print(f"[ERROR] Exception in bot loop: {e}")
                time.sleep(2)


if __name__ == "__main__":
    bot = OpenAIBot("http://flask-app:5000", name="OpenAI Bot")
    bot.play()






