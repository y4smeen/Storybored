from flask import Flask, render_template, request, session, redirect, url_for
import database
import user
'''
Session['logged'] determines whether someone is logged in
0 means logged out
1 means logged in



'''

DATABASE = 'storybored'
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


def id_to_name(user):
	return database.get_user_by_id(user)

app = Flask(__name__)
app.jinja_env.filters['idtoname'] = id_to_name

@app.route('/')
@app.route("/home/")
def home():
  # session["logged"] = 0
  	if (not "logged" in session):
  		session["logged"] = 0
	return render_template("home.html")

@app.route("/login/", methods=['GET', 'POST'])
def login():
  #  session["logged"] = 0
    if request.method=="GET":
        return render_template("login.html")
    else:
        if request.form["sub"]=="Cancel":
            return render_template("login.html")
        user = database.check_user_password(request.form["username"], request.form["password"])
        if user > 0:
            session["user"] = user
            session["logged"] = 1
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
        database.add_user(request.form["user"], request.form["pass"])
        return redirect(url_for("login"))


@app.route("/userpage/")
def userpage():
    if session["logged"]==0:
        return redirect(url_for("login"))
    else:
        return render_template("userpage.html",
        uname=database.get_user_by_id(session["user"]),
        posts=reversed(database.get_top_posts(-1)),
        yourposts=database.get_top_posts(session["user"]))

@app.route("/newpost/", methods=['GET', 'POST'])
def newpost():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        username = database.get_user_by_id(session["user"])
        return render_template("newpost.html", uname=username)
    else:
        title = request.form["title"]
        body = request.form["body"]
        session["title"] = title
        session["body"] = body
        session["author"] = database.get_user_by_id(session["user"])
        return redirect(url_for("story", storyid=database.add_story(title, session["user"], body, 1)))

@app.route("/edit/", methods=["GET","POST"])
def edit():
    if session["logged"]==0:
        return redirect(url_for("login"))
    elif request.method=="GET":
        username = database.get_user_by_id(session["user"])
        return render_template("edit.html", uname=username)
    else:
        title = "<NO TITLE YET>"
        database.update_story_link(database.get_lowest_child(request.args.get('storyid')), database.add_story(title, session["user"], request.form["body"], 0))
        return redirect(url_for('story', storyid=request.args.get('storyid')))

@app.route("/story/")
def story():
    if session["logged"]==0:
        return redirect(url_for("login"))
    return render_template("story.html",
        title="POSTS", author="",
        posts=database.get_top_posts(-1),
        uname=database.get_user_by_id(session["user"]),
        storyid=request.args.get('storyid'),
        content=database.get_story_content(request.args.get('storyid')))

@app.route("/deletepost/")
def deletepost():
    if session["logged"]==0:
        return redirect(url_for("login"))
    database.remove_story(request.args.get('storyid'))
    return redirect(url_for("userpage"))

@app.route("/deleteline/")
def deleteline():
    if session["logged"]==0:
        return redirect(url_for("login"))
    return redirect(url_for("userpage"))

@app.route("/logout/")
def logout():
    session['logged'] = 0
    session.pop('userid', None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "STORYBORED"
    app.run('0.0.0.0',port=8000)
