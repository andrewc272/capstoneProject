from flask import *
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "dev_fallback_secret_key")

active_users = []

turn_index = 0

# TODO move this to a separate file as a sort of "game state object"
gamePhase = ["intro", "lobby", "chat", "guess", "results"]
chats = []
current_phase_index = 0
turnID = None

@app.before_request
def assignSessionID():
    """This assigns a user ID to each player that connects"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route("/")
def getPage():
    """
        Packs and sends the frontend to the user.

        Returns:
            HTML: the rendered index.html file
    """
    return render_template("index.html")

@app.route("/gameState", methods=["GET", "POST"])
def gameState():
    """
        GETs and POSTs to the gameState

        Args:
            request: used for method and getting data for post

        Returns:
            JSON: either returning the status or the gameState
    """
    global current_phase_index, chats, turnID, turn_index

    if request.method == "GET":
        # Auto-advance after 10 messages
        if len(chats) >= 10:
            current_phase_index = min(current_phase_index + 1, len(gamePhase) - 1)
            chats.clear()
            turn_index = 0

        # ---- FIXED TURN FORMULA ----
        if len(active_users) > 0:
            turnID = active_users[turn_index % len(active_users)]

        currentPhase = gamePhase[current_phase_index]

        data = {
            "gamePhase": currentPhase,
            "chats": chats,
            "myId": session["user_id"],
            "turnID": turnID,
            "users": list(active_users)
        }

        print(data)
        return jsonify(data)

    elif request.method == "POST":
        data = request.get_json()
        if data.get("nextPhase") == True:
            if current_phase_index == 1:
                turnID = active_users[0] if active_users else None
            current_phase_index = min(current_phase_index + 1, len(gamePhase) - 1)
            turn_index = 0

        print("Received via POST:", data)
        return jsonify(status="ok")

@app.route("/addPlayer", methods=["GET"])
def addPlayer():
    """This adds joins the player to the game and should be called when a player wants to join a game"""
    uid = session['user_id']
    if uid not in active_users:
        active_users.append(uid)
    return jsonify(status="ok")

@app.route("/removePlayer", methods=["POST"])
def removePlayer():
    uid = session.get('user_id')
    global turn_index, turnID
    if uid in active_users:
        idx = active_users.index(uid)
        active_users.remove(uid)
        if idx < turn_index:
            turn_index -= 1
        elif idx == turn_index:
            turn_index = turn_index % len(active_users) if active_users else 0
        turnID = active_users[turn_index] if active_users else None
    return jsonify(status="ok")

@app.route("/message", methods=["POST"])
def addMessage():
    """
        Receives messages and updates the chatlog

        Args:
            request: used to obtain the message

        Returns:
            a redirect to "/" (to be changed)
    """
    global turnID, turn_index
    user_id = session.get('user_id')
    data = request.get_json()

    if not active_users:
        return jsonify(status="no_users")

    if user_id != turnID:
        chats.append((user_id, "Played out of turn"))
        return jsonify(status="ok")

    chats.append((user_id, data.get("message")))
    turn_index = (turn_index + 1) % len(active_users)
    turnID = active_users[turn_index]
    return jsonify(status="ok")


