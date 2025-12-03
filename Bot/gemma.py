import requests
import time
import os
from dotenv import load_dotenv
from ollama import chat as chatGemma
from ollama import ChatResponse

load_dotenv()


class GemmaBot:
    def __init__(self, url, name="Gemma Bot"):
        self.url = url.rstrip("/")
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({"X-Bot-Name": self.name})
        self.myID = None
        self.added = False

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
                '''
                You exist as a Human player in a chat game.
                You are to respond to previous chats and continue the conversation well.
                You are to responde breifly and casually.
                The length of your response should be no longer than a sentence.
                It is urgent that you are not detected so act like a human as best you can. 
                Change your grammar and spelling slightly rarely.
                If you get caught bad things could happen so again DO NOT GET CAUGHT.
                If you are in a pinch there are two options you have either you can try to change the topic SLIGHTLY or you can shift the blame.
                '''
        )

        if not chats:
            conversation = ""
        else:
            conversation = ""
            for uid, msg in chats:
                speaker = "" if uid == self.myID else f"Player {uid[:4]}"
                conversation += f"{speaker}: {msg}\n"

        prompt = conversation + f"{self.name}:"

        response = chatGemma(model='gemma3',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']


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
    bot = GemmaBot("http://localhost:5000", name="Ollama Bot")
    bot.play()






