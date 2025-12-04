import os
import random
import re
import textwrap
import time
from typing import List

import requests

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bot import Bot
from bot_profiles import DEFAULT_LOCAL_MODEL, LOCAL_BOT_PRESETS


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

# Human names the bot can use when asked
BOT_NAMES = ["Jordan", "Riley", "Casey", "Morgan", "Taylor", "Jamie", "Quinn", "Avery"]



def trim_history(chats: List[list], keep_last: int = 10):
    if keep_last <= 0:
        return chats
    return chats[-keep_last:]


def render_history(chats, my_id):
    lines = []
    for uid, message in chats:
        speaker = "You" if uid == my_id else f"Player-{uid[:4]}"
        text = message or ""
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)


def latest_non_self_message(chats, my_id):
    for uid, message in reversed(chats):
        if uid != my_id:
            return message or ""
    return chats[-1][1] if chats else ""


class LocalAgent(Bot):
    def __init__(self):
        profile_id = os.getenv("LOCAL_AGENT_PROFILE", DEFAULT_LOCAL_MODEL)
        self.profile = LOCAL_BOT_PRESETS.get(profile_id, LOCAL_BOT_PRESETS[DEFAULT_LOCAL_MODEL])
        name = os.getenv("LOCAL_AGENT_NAME", f"local-{profile_id}")
        server_url = os.getenv("CAPSTONE_SERVER_URL", "http://127.0.0.1:5000")
        self.last_sent = None

        # Pick a human name for this bot to use in conversation
        self.human_name = random.choice(BOT_NAMES)

        print(f"[LocalAgent] {name} using preset '{self.profile['id']}' -> model '{self.profile['model']}'")
        print(f"[LocalAgent] Human name: {self.human_name}")
        super().__init__(name=name, url=server_url)

    def get_message(self, chats=[]):
        chats = chats or []
        trimmed = trim_history(chats, self.profile["context_window"])
        history = render_history(trimmed, self.my_id)
        latest = latest_non_self_message(trimmed, self.my_id)

        latest_lower = (latest or "").lower().strip()
        is_name_question = any(x in latest_lower for x in [
            "your name", "what's your name", "whats your name", "who are you"
        ])

        guidance = [
            f"You are {self.human_name}, a believable college student hanging out in a group chat.",
            "Keep the tone natural and varied – some replies can be short, others can be a couple sentences.",
            "React to the actual conversation instead of repeating generic filler.",
            "It is fine to show opinions, humor, or mild emotion if the moment calls for it."
        ]
        if is_name_question:
            guidance.append(f"Someone asked your name. Casually tell them you're {self.human_name}.")

        prompt = textwrap.dedent(
            f"""
            {" ".join(guidance)}

            Group chat log (most recent last):
            {history}

            Last message you saw: "{latest}"

            Reply as {self.human_name}. If you answer a question, provide enough detail to sound human.
            End with just the text you would send.
            """
        ).strip()

        if self.profile["engine"] == "ollama":
            reply = self._ollama_reply(prompt)
            if reply:
                reply = self._clean_reply(reply, chats)
                if reply and reply != self.last_sent:
                    self._human_delay(latest, reply)
                    self.last_sent = reply
                    return reply

        return None

    def _clean_reply(self, reply: str, chats: list) -> str:
        """Clean up the reply and check for obvious copies."""
        reply = reply.strip().strip('"').strip("'")

        # Remove "Player-XXXX:" or "You:" prefixes the bot might copy from history format
        reply = re.sub(r'^(Player-[a-zA-Z0-9]+|You)\s*:\s*', '', reply, flags=re.IGNORECASE)

        # Remove name prefixes like "Jordan:" if bot includes its own name
        reply = re.sub(r'^[A-Z][a-z]+\s*:\s*', '', reply)

        reply = reply.strip()

        # Remove common AI-ish prefixes
        prefixes_to_remove = [
            "Sure!", "Of course!", "Hey there!", "Well,", "So,", "I think",
            "As a", "I'm just", "Actually,", "Honestly,"
        ]
        for prefix in prefixes_to_remove:
            if reply.startswith(prefix):
                reply = reply[len(prefix):].strip()
                if reply and reply[0].islower():
                    reply = reply[0].upper() + reply[1:]

        return reply if reply else None

    def _ollama_reply(self, prompt: str):
        payload = {
            "model": self.profile["model"],
            "messages": [
                {"role": "system", "content": self.profile["prompt"]},
                {"role": "user", "content": prompt},
            ],
            "options": {
                "temperature": self.profile["temperature"],
                "num_predict": self.profile["max_tokens"],
            },
            "stream": False,
        }

        try:
            response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {}).get("content")
            if message:
                return message.strip()
        except Exception:
            return None
        return None

    def _human_delay(self, latest_message: str, reply: str):
        """Sleep to simulate thinking/typing time based on message length."""
        latest_len = len(latest_message or "")
        reply_len = len(reply or "")
        think_time = 0.6 + (latest_len / 80.0)
        type_speed = random.uniform(12, 20)  # characters per second
        type_time = reply_len / type_speed
        jitter = random.uniform(0.5, 1.4)
        delay = (think_time + type_time) * jitter
        delay = max(0.8, min(delay, 6.0))
        time.sleep(delay)

if __name__ == "__main__":
    agent = LocalAgent()
    agent.run()
