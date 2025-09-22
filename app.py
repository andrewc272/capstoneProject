from flask import *
import time

app = Flask(__name__)

gamePhase = ["lobby", "chat", "guess", "results"]
chats = []
current_phase_index = 0

@app.route("/", methods=["GET", "POST"])
def getPage():
    return render_template("index.html")


@app.route("/gameState", methods=["GET", "POST"])
def gameState():
    global current_phase_index

    if request.method == "GET": # GET: /gameState
        index = int(time.time() / 5) % len(gamePhase)
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
    if request.method == "POST":
        message= request.form.get("message")
        print(f'Message received: {message}')
        chats.append(message)
    return redirect("/")

# Resolves ERROR 404 /favicon.ico not found
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content

