from flask import Flask, render_template, request, session, redirect, url_for
from database import Database
import user

DATABASE = './database.db'
SCHEMA = [
    (u'CREATE TABLE stories (title text, author text, contents text, postid int, nextlink int)',),
    (u'CREATE TABLE users (username text, password blob)',)
    ]

db = Database(DATABASE, SCHEMA)
postid = 0

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
        sub   = request.form["sub"]
        if request.form["sub"]=="Cancel":
            return render_template("login.html")
        elif user.authenticate(uname, pword):
            session["uname"]=uname
            session["logged"]=1
            return redirect(url_for("userpage"))
        else:
            error = "You have entered an incorrect username or password.\n"
            return render_template("login.html", error=error)
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        return redirect(url_for("confirm"))

@app.route("/confirm")
def confirm():
    return redirect(url_for("login"))

@app.route("/userpage")
def userpage():
    if session["logged"]==0:
        return redirect(url_for("login"))
    else:
        username = session["uname"]
        return render_template("userpage.html",uname=username)

@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        return render_template("newpost.html")
    else:
        #print("sending post stuff through")
        title = request.form["title"]
        body = request.form["body"]
        username = session["uname"]
        sub = request.form["sub"]
        session["title"] = title
        session["body"] = body
        session["author"] = username
        db.add_story(title, username, body, postid, -1)
        return redirect(url_for("story"))

@app.route("/edit", methods=["GET","POST"])
def edit():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        return render_template("edit.html")
    else:
        oldid = postid
        newid = postid+1
        db.update_story(oldid,newid)
                
        body = request.form["newline"]
        username = session["uname"]
        sub = request.form["sub"]
        db.add_story(title, username, body, newid, -1)
        content_list = db.get_content
        return redirect(url_for("story"), title=title, author=username, content_list=content_list)


@app.route("/story")
def story():
    if session["logged"]==0:
        return redirect(url_for("login"))
    else:
        return render_template("story.html")


@app.route("/logout")
def logout():
    session["username"]=""
    session["logged"]=0
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "STORYBORED"
    app.run('0.0.0.0',port=8000)
