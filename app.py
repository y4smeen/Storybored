from flask import Flask, render_template, request, session, redirect, url_for
from database import Database, format_schema
import user

DATABASE = './database.db'
SCHEMA = [
    ('stories', [
        ('title', 'text'),
        ('author', 'int'),
        ('contents', 'text'),
        ('link', 'int'),
        ('istop','int'),
    ]),
    ('users', [
        ('username', 'text'),
        ('password', 'blob'),
    ]),
]

db = Database(DATABASE, SCHEMA)

def id_to_name(user):
    return db.get_user_by_id(user)

app = Flask(__name__)
app.jinja_env.filters['idtoname'] = id_to_name

@app.route('/')
@app.route("/home/")
def home():
    return render_template("home.html")

@app.route("/login/", methods=['GET', 'POST'])
def login():
    session["logged"] = 0
    if request.method=="GET":
        return render_template("login.html")
    else:
        if request.form["sub"]=="Cancel":
            return render_template("login.html")
        user = db.check_user_password(request.form["username"], request.form["password"])
        if user > 0:
            session["user"] = user
            session["logged"]=1
            return redirect(url_for("userpage"))
        else:
            error = "You have entered an incorrect username or password.\n"
            return render_template("login.html", error=error)
        return render_template("login.html")

@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        session["uname"] = request.form["user"]
        db.add_user(request.form["user"], request.form["pass"])
        return redirect(url_for("confirm"))

@app.route("/confirm/")
def confirm():
    return redirect(url_for("login"))

@app.route("/userpage/")
def userpage():
    if session["logged"]==0:
        return redirect(url_for("login"))
    else:
        username = db.get_user_by_id(session["user"])
        return render_template("userpage.html",uname=username)

@app.route("/newpost/", methods=['GET', 'POST'])
def newpost():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        username = db.get_user_by_id(session["user"])
        return render_template("newpost.html", uname=username)
    else:
        #print("sending post stuff through")
        title = request.form["title"]
        body = request.form["body"]
        session["title"] = title
        session["body"] = body
        session["author"] = db.get_user_by_id(session["user"])
        session["recentid"]=1
        db.add_story(title, session["user"], body, 1)
        return redirect(url_for("story"))

@app.route("/edit/", methods=["GET","POST"])
def edit():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        username = db.get_user_by_id(session["user"])
        return render_template("edit.html", uname=username)
    else:
        title = "<NO TITLE YET>"
        db.update_story_link(db.get_lowest_child(request.args.get('storyid')), db.add_story(title, session["user"], request.form["body"], 0))
        return redirect(url_for("story"))

@app.route("/story/")
def story():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("story.html",
            title="POSTS", author="",
            posts=db.get_top_posts(),
            uname=db.get_user_by_id(session["user"]),
            storyid=request.args.get('storyid'),
            content=db.get_story_content(request.args.get('storyid')))
    else:
        username = db.get_user_by_id(session["user"])
        print(db.get_content())
        print(len(db.get_content()))
        print(db.get_users())
        print()
        return render_template("story.html", title=session["title"], author=db.get_user_by_id(session["user"]), posts=db.get_top_posts())


@app.route("/logout/")
def logout():
    session["username"]=""
    session["logged"]=0
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "STORYBORED"
    app.run('0.0.0.0',port=8000)
