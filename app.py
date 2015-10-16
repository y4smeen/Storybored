
from flask import Flask, render_template, request, session, redirect, url_for
import user

app = Flask(__name__)
@app.route('/')
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    session["logged"] = 0
    if request.method=="GET":
        return render_template("login.html")
    else:
        uname = request.form["username"]
        pword = request.form["password"]
        sub      = request.form["sub"]
        if user.authenticate(uname, pword):
            session["uname"]=uname
            session["logged"]=1
            return redirect(url_for("userpage"))
        else:
            return "You have entered an incorrect username or password <hr> Click <a href = '/login'> here </a> to go back to login page." #TODO: make an html page for this
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        return redirect(url_for("confirm"))

@app.route("/confirm")
def confirm():
    return render_template("confirm.html")

@app.route("/userpage")
def userpage():
    uname = session["uname"]
    return render_template("userpage.html",uname=uname)

@app.route("/newpost")
def newpost():
    return render_template("newpost.html")

@app.route("/story")
def story():
    return render_template("story.html")

@app.route("/logout")
def logout():
    session["username"]=""
    session["logged"]=0
    return redirect(url_for("home"))
    
@app.route("/temp/")
def temp():
    return render_template("temp/home.html", index=True)
    
@app.route("/temp/login/")
def temp_login():
    return render_template("temp/login.html")

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "STORYBORED"
    app.run('0.0.0.0',port=8000)
