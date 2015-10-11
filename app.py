
from flask import Flask, render_template, request, session, url_for


app = Flask(__name__)
@app.route('/')
@app.route("/home")
def about():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    session["logged"] = 0
    if request.method=="GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        sub      = request.form["sub"]
        return render_template("login.html")

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "STORYBORED"
    app.run('0.0.0.0',port=8000)
