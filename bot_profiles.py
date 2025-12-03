LOCAL_BOT_PRESETS = {
    "pocket": {
        "id": "pocket",
        "label": "Pocket Chat (Ultralight)",
        "description": "Cautious tone that relaxes as the chat continues.",
        "hardware": "Runs on most modern CPUs.",
        "engine": "ollama",
        "model": "llama3.2:1b",
        "temperature": 0.7,
        "max_tokens": 250,
        "context_window": 100000,
        "prompt": (
            "You are a college student. Reply naturally to what others say. "
            "Stay on the current topic. Be brief."
        )
    },
    "lounge": {
        "id": "lounge",
        "label": "Campus Lounge (Laptop)",
        "description": "Balanced replies that closely track human tone.",
        "hardware": "Best with 16GB RAM laptop or Apple Silicon.",
        "engine": "ollama",
        "model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 250,
        "context_window": 100000,
        "prompt": (
            "You are a college student in a group chat. Respond to what people actually said. "
            "Stay on topic. Keep it casual and short."
        )
    },
    "studio": {
        "id": "studio",
        "label": "Studio 8G (GPU)",
        "description": "High-context replies with calm skepticism.",
        "hardware": "Needs ~8GB dedicated GPU or beefy CPU.",
        "engine": "ollama",
        "model": "llama3.1:8b",
        "temperature": 0.7,
        "max_tokens": 250,
        "context_window": 100000,
        "prompt": (
            "You are a college student chatting with friends. Pay attention to the conversation "
            "and respond to what was just said. Stay on topic. Be natural and concise."
        )
    }
}

DEFAULT_LOCAL_MODEL = "pocket"
