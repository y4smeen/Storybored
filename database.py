from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class Database:
    def __init__(self, database, schema):
        self.db = db = sqlite3.connect(database)
        self.c = c = db.cursor()
        print " !- Connecting to databse'" + database + "'..."
        if c.execute("SELECT sql FROM sqlite_master WHERE type='table';").fetchall() != schema:
            print " !- Invalid database schema! Dropping everything and recreating."
            for table in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
                print " !-- Dropping table " + table + "..."
                c.execute("DROP TABLE " + table[0] + ";")
            for statement in schema:
                print " !-- Execute: (" + statement[0] + ";)"
                c.execute(statement[0] + ";")
        else:
            print " !- Valid database schema. Carry on."
    
    def add_story(self, title, author, contents):
        self.c.execute("INSERT INTO stories VALUES(?, ?, ?);", (title, author, contents))
        self.db.commit()
    
    def add_user(self, username, password):
        password = generate_password_hash(password)
        self.c.execute("INSERT INTO users VALUES(?, ?);", (username, password))
        self.db.commit()

    def update_user_password(self, username, new_password):
        password = generate_password_hash(new_password)
        self.c.execute("UPDATE users SET password=(?) WHERE username=(?);", (password, username))
        self.db.commit()
    
    def get_stories(self):
        stories = []
        for story in self.c.execute("SELECT title FROM stories").fetchall():
            stories.append(story[0])
        return stories
    
    def get_users(self):
        users = []
        for user in self.c.execute("SELECT username FROM users").fetchall():
            users.append(user[0])
        return users

    def check_user_password(self, username, password):
        password_hash = self.c.execute("SELECT password FROM users WHERE username=(?);", (username,)).fetchall()[0][0]
        return check_password_hash(password_hash, password)
    
