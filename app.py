"""
app.py

Web API implemented with flask
"""

from flask import *
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# TODO move this to a sperate file as a sort of "game state object"
gamePhase = ["lobby", "chat", "guess", "results"]
chats = []
current_phase_index = 0

@app.before_request
def assignSessionID():
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
    global current_phase_index

    if request.method == "GET": # GET: /gameState
        currentPhase = gamePhase[current_phase_index]
        data = {
            "gamePhase": currentPhase,
            "chats" : chats
        }
        return jsonify(data)

    elif request.method == "POST": # POST: /gameState
        data = request.get_json()
        if data.get("nextPhase") == True:
            current_phase_index = (current_phase_index + 1) % len(gamePhase)
        print("Received via POST:", data)
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
    # TODO will need to be changed to obtain JSON data and return status "OK"
    if request.method == "POST":
        user_id = session.get('user_id')
        data = request.get_json()
        chats.append((user_id, data.get("message")))
        return jsonify(status="ok")
