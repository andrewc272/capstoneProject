from flask import *
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_fallback_secret_key")


class Player:
    def __init__(self, user_id, is_a_bot):
        self.user_id = user_id
        self.votes = 0
        self.is_a_bot = is_a_bot


players = {}
active_users = []

gamePhase = ["intro", "lobby", "chat", "guess", "results"]
current_phase_index = 0

chats = []
turn_index = 0
turnID = None
votes_submitted = 0


@app.before_request
def assignSessionID():
    bot_header = request.headers.get("X-Bot-Name")
    if bot_header:
        g.user_id = bot_header
        return
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
        if len(chats) >= 10:
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
        player_list = [{"user_id": p.user_id, "votes": p.votes, "is_a_bot": p.is_a_bot} for p in players.values()]

        return jsonify({
            "gamePhase": currentPhase,
            "chats": chats,
            "myId": g.user_id,
            "turnID": turnID,
            "users": active_users,
            "players": player_list
        })

    data = request.get_json()
    if data.get("nextPhase"):
        current_phase_index = min(current_phase_index + 1, len(gamePhase) - 1)
        if gamePhase[current_phase_index] == "chat":
            turn_index = 0
            turnID = active_users[0] if active_users else None
        if gamePhase[current_phase_index] == "guess":
            votes_submitted = 0
    print("Current phase:", gamePhase[current_phase_index])

    return jsonify(status="ok")


@app.route("/addPlayer", methods=["GET"])
def addPlayer():
    uid = g.user_id

    # Detect bots using the same header as before_request
    is_a_bot = "X-Bot-Name" in request.headers

    if uid not in active_users and len(active_users) <= 6:
        active_users.append(uid)

    if uid not in players and len(players) <= 6:
        players[uid] = Player(uid, is_a_bot)  # Pass true for bots

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
    global current_phase_index, votes_submitted
    data = request.get_json()

    # { "votes": [ { "target": "<user_id>", "guess": "human"|"ai" }, ... ] }
    votes = data.get("votes", [])

    for vote in votes:
        target = vote.get("target")
        guess = vote.get("guess")

        # increment votes for AI guesses
        if guess == "ai" and target in players:
            players[target].votes += 1

    votes_submitted = votes_submitted + 1

    # minus 2 to remove the bots having to vote
    if votes_submitted == len(players) - 2:
        current_phase_index = 4

    return jsonify(status="ok")

@app.route("/resetGame", methods=["POST"])
def resetGame():
    global players, active_users, current_phase_index, chats, turn_index, turnID, votes_submitted

    # Keep only the bots
    kept_users = active_users[:2]

    # Rebuild players dict using the original bot flags
    new_players = {}
    for uid in kept_users:
        if uid in players:
            new_players[uid] = Player(uid, players[uid].is_a_bot)
        else:
            # fallback if somehow missing
            new_players[uid] = Player(uid, True)

    players = new_players

    # Reset active users
    active_users = kept_users

    # Reset game state
    current_phase_index = 0   # back to "intro"
    chats = []
    votes_submitted = 0
    turn_index = 0
    turnID = kept_users[0] if kept_users else None

    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)






