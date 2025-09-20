from flask import *
import time

app = Flask(__name__)

gamePhase = ["lobby", "chat", "guess", "results"]
current_phase_index = 0

@app.route("/", methods=["GET", "POST"])
def getPage():
    return render_template("index.html")


@app.route("/gameState", methods=["GET", "POST"])
def gameState():
    global current_phase_index

    if request.method == "GET": # GET: /gameState
        index = int(time.time() / 5) % len(gamePhase)
        currentPhase = gamePhase[index]

        data = {
            "gamePhase": currentPhase
        }
        return jsonify(data)

    elif request.method == "POST": # POST: /gameState
        data = request.get_json()
        if data.get("nextPhase") == True:
            current_phase_index = (current_phase_index + 1) % len(gamePhase)
        print("Received via POST:", data)
        return jsonify(status="ok")
