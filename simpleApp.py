from flask import Flask, request, make_response

app = Flask(__name__)

@app.route("/")
def hello_world():
    username = request.cookies.get('username')
    if username == None:
        resp = make_response()
        username = '92837423'
        resp.set_cookie('username', username)
        return resp
    return f'Hello, {username}!'
    

@app.route("/user")
def show_username():
    username = request.cookies.get('username')
    return f'User {username}'

@app.route("/setuser", methods=['GET', 'POST'])
def setUser():
   pass 

    

@app.route("/messaging", methods=['GET', 'POST'])
def message():
    chat = ""
    with open("chatlog.txt", "r", encoding="utf-8") as f:
              chat = f.read()

    if request.method == "POST":
        chat = chat + f'<p>{request.form['message']}</p>'
        with open("chatlog.txt", "w", encoding="utf-8") as f:
                  f.write(chat)
    return chat + '''
    <form method="post">
            <p><input type=text name=message>
            <p><input type=submit value=Send>
        </form>
    '''
