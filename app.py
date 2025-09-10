from flask import *

app = Flask(__name__)

chatlog = []

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        chatlog.append(request.form['message'])
    print(chatlog)
    return render_template("index.html", chatlog=chatlog)
