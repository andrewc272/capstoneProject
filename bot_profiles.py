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
            "Stay on the current topic. Be brief. Use context from earlier in the chat to inform your responses."
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
            "You are a college student. Reply naturally to what others say. "
            "Stay on the current topic. Be brief. Use context from earlier in the chat to inform your responses."
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
            "You are a college student. Reply naturally to what others say. "
            "Stay on the current topic. Be brief. Use context from earlier in the chat to inform your responses."
        )
    }
}

DEFAULT_LOCAL_MODEL = "pocket"
