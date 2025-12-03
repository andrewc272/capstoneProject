import atexit
import os
import uuid
from pathlib import Path

from flask import *
from dotenv import load_dotenv

from bot_manager import LocalBotManager
from bot_profiles import DEFAULT_LOCAL_MODEL, LOCAL_BOT_PRESETS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_fallback_secret_key")


class Player:
    def __init__(self, user_id, is_bot=False):
        self.user_id = user_id
        self.votes = 0
        self.is_bot = is_bot


players = {}
active_users = []

gamePhase = ["intro", "lobby", "chat", "guess", "results"]
current_phase_index = 0

chats = []
turn_index = 0
turnID = None
votes_submitted = 0
votes_recorded = set()

host_id = None

bot_settings = {
    "mode": "cloud_api",
    "local_model": DEFAULT_LOCAL_MODEL,
    "local_count": 1,
}

LOCAL_SERVER_URL = os.getenv("LOCAL_BOT_SERVER_URL", "http://127.0.0.1:5000").rstrip("/")
BOT_MANAGER_DISABLED = os.getenv("CAPSTONE_SKIP_BOT_MANAGER") == "1"
project_dir = Path(__file__).resolve().parent
bot_manager = LocalBotManager(project_dir, disabled=BOT_MANAGER_DISABLED)
atexit.register(bot_manager.stop)


def reset_state():
    """Utility to reset global state (used by tests)."""
    global players, active_users, current_phase_index, chats, turn_index, turnID
    global votes_submitted, votes_recorded, host_id, bot_settings

    players = {}
    active_users = []
    current_phase_index = 0
    chats = []
    turn_index = 0
    turnID = None
    votes_submitted = 0
    votes_recorded = set()
    host_id = None
    bot_settings = {
        "mode": "cloud_api",
        "local_model": DEFAULT_LOCAL_MODEL,
        "local_count": 1,
    }
    bot_manager.stop()


def serialize_model_options():
    return [
        {
            "id": preset["id"],
            "label": preset["label"],
            "description": preset["description"],
            "hardware": preset["hardware"],
        }
        for preset in LOCAL_BOT_PRESETS.values()
    ]


def ensure_host_present():
    """Ensure host_id points to the first human player if available."""
    global host_id
    if host_id in players and not players[host_id].is_bot:
        return
    host_id = None
    for uid in active_users:
        player = players.get(uid)
        if player and not player.is_bot:
            host_id = uid
            break


def apply_host_configuration(data):
    global bot_settings
    if not data:
        return

    changed = False
    mode = data.get("botMode")
    if mode in {"cloud_api", "local_ai"} and bot_settings["mode"] != mode:
        bot_settings["mode"] = mode
        changed = True

    model = data.get("localModel")
    if model in LOCAL_BOT_PRESETS and bot_settings["local_model"] != model:
        bot_settings["local_model"] = model
        changed = True

    # Hardcoded to 1 bot for now while perfecting behavior
    bot_settings["local_count"] = 1

    if changed:
        sync_local_bots()


def sync_local_bots():
    if bot_settings["mode"] != "local_ai":
        bot_manager.ensure_state("", 0, LOCAL_SERVER_URL)
        return
    profile_id = bot_settings.get("local_model", DEFAULT_LOCAL_MODEL)
    # Hardcoded to 1 bot while perfecting behavior
    bot_manager.ensure_state(profile_id, 1, LOCAL_SERVER_URL)


@app.before_request
def assignSessionID():
    bot_header = request.headers.get("X-Bot-Name")
    if bot_header:
        g.user_id = bot_header
        g.is_bot = True
        return
    g.is_bot = False
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    g.user_id = session["user_id"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gameState", methods=["GET", "POST"])
def gameState():
    global current_phase_index, chats, turn_index, turnID, votes_submitted

    if request.method == "GET":
        if len(chats) >= 20:
            chats = []
            current_phase_index = min(current_phase_index + 1, len(gamePhase) - 1)

        if active_users:
            if gamePhase[current_phase_index] == "chat":
                if turnID not in active_users:
                    turn_index = 0
                    turnID = active_users[0]
            else:
                turnID = None
        else:
            turnID = None

        currentPhase = gamePhase[current_phase_index]
        player_list = [
            {"user_id": p.user_id, "votes": p.votes, "isBot": p.is_bot}
            for p in players.values()
        ]

        return jsonify({
            "gamePhase": currentPhase,
            "chats": chats,
            "myId": g.user_id,
            "turnID": turnID,
            "users": active_users,
            "players": player_list,
            "hostId": host_id,
            "isHost": g.user_id == host_id,
            "botMode": bot_settings["mode"],
            "localModel": bot_settings["local_model"],
            "localBotCount": bot_settings["local_count"],
            "modelOptions": serialize_model_options(),
            "botStatus": bot_manager.status(),
        })

    data = request.get_json() or {}
    if not g.is_bot and (host_id is None or g.user_id == host_id):
        apply_host_configuration(data)

    if data.get("nextPhase") and host_id and not g.is_bot and g.user_id != host_id:
        return jsonify(status="forbidden"), 403

    if data.get("nextPhase"):
        current_phase_index = min(current_phase_index + 1, len(gamePhase) - 1)
        if gamePhase[current_phase_index] == "chat":
            turn_index = 0
            turnID = active_users[0] if active_users else None
        if gamePhase[current_phase_index] == "guess":
            votes_submitted = 0
            votes_recorded.clear()
    print("Current phase:", gamePhase[current_phase_index])

    return jsonify(status="ok")


@app.route("/addPlayer", methods=["GET"])
def addPlayer():
    uid = g.user_id
    if uid not in active_users:
        active_users.append(uid)
    if uid not in players:
        players[uid] = Player(uid, is_bot=getattr(g, "is_bot", False))
    ensure_host_present()
    return jsonify(status="ok")


@app.route("/removePlayer", methods=["POST"])
def removePlayer():
    global turn_index, turnID
    uid = g.user_id

    if uid in active_users:
        idx = active_users.index(uid)
        active_users.remove(uid)
        if uid in players:
            del players[uid]

        if not active_users:
            turn_index = 0
            turnID = None
        else:
            if idx < turn_index:
                turn_index -= 1
            elif idx == turn_index:
                turn_index = turn_index % len(active_users)
            turnID = active_users[turn_index]

    ensure_host_present()
    if host_id is None:
        bot_manager.stop()

    return jsonify(status="ok")


@app.route("/message", methods=["POST"])
def addMessage():
    global turn_index, turnID

    user_id = g.user_id
    if user_id != turnID:
        chats.append((user_id, "Played out of turn"))
        return jsonify(status="ok")

    data = request.get_json()
    chats.append((user_id, data.get("message", "")))

    if active_users:
        turn_index = (turn_index + 1) % len(active_users)
        turnID = active_users[turn_index]

    return jsonify(status="ok")


@app.route("/vote", methods=["POST"])
def vote():
    global current_phase_index, votes_submitted, votes_recorded
    if getattr(g, "is_bot", False):
        return jsonify(status="ok")

    data = request.get_json() or {}
    uid = g.user_id
    
    if uid in votes_recorded:
        return jsonify(status="ok")

    votes = data.get("votes", [])

    for vote_payload in votes:
        target = vote_payload.get("target")
        guess = vote_payload.get("guess")

        # increment votes for AI guesses 
        if guess == "ai" and target in players:
            players[target].votes += 1

    votes_recorded.add(uid)
    votes_submitted = len(votes_recorded)

    human_players = [p for p in players.values() if not p.is_bot]
    if votes_submitted >= len(human_players) and human_players:
        current_phase_index = len(gamePhase) - 1

    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)






