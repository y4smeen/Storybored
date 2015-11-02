"""StoryBored SQLite database handler module.

Allows for database communication. Instantiate with:

    db = Database(<path to database>, <schema>)

Schemas should be formatted as follows:

    SCHEMA = [
        ('<table1>', [
            ('<col1>', 'type'),
            ('<col2>', 'type'),
            ...
        ]),
        ('<table2>', [
            ('<col1>', 'type'),
            ('<col2>', 'type'),
            ...
        ]),
        ...
    ]
"""

from werkzeug.security import generate_password_hash, check_password_hash
# import sqlite3
from pymongo import MongoClient

class Database:
    """StoryBored main database handler class.

    Attributes:
        db (sqlite3 connection): The sqlite3 connection to the database.
        c (sqlite3 Cursor): The Cursor that can be used to send statements to
            the sqlite3 database.

    """
    # def __init__(self, database, schema):
    #     #p sure we don't need this
        

    #     """StoryBored Database __init__.

    #     Args:
    #         database (str): Path to the sqlite3 database.
    #         schema (schema_statement): Schema to be applied to the
    #             database.

    #     If the database's schema does not match the one provided by the schema
    #     statement, all of the database's tables will be dropped and it will be
    #     recrated with the appropriate tables and data.
    #     """
    #     # self.db = db = sqlite3.connect(database, check_same_thread=False)
    #     # self.c = c = db.cursor()
        
    #     print " !- Connecting to database'" + database + "'..."
    #     schema = format_schema(schema)
    #     if c.execute("SELECT sql FROM sqlite_master WHERE type='table';").fetchall() != schema:
    #         print " !- Invalid database schema! Dropping everything and recreating."
    #         for table in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall():
    #             print " !-- Dropping table " + table[0] + "..."
    #             c.execute("DROP TABLE " + table[0] + ";")
    #         for statement in schema:
    #             print " !-- Execute: (" + statement[0] + ";)"
    #             c.execute(statement[0] + ";")
    #     else:
    #         print " !- Valid database schema. Carry on."
    def __init__(self, database):
    	connection = MongoClient()
        db = connection[database]
        print " !- Connecting to database'" + database + "'..."

    def add_story(self, title, author, contents, istop):
        rid = get_next_rowid() + 1
        db.stories.insert({'title':title,
                           'author': author,
                           'contents':contents,
                           'link':-1,
                           'rowid': rid,
                           'istop': istop})
        return rid
         

    #~used to link lines together based on rowid
    #~link = rowid of nextline
    def update_story_link(self, story, link):
        #~if rowid = story, link = link
        db.stories.update({ 'rowid' : story },
                          { '$set' : { 'link' : link } })

    #~gets highest rowid in stories
    def get_next_rowid(self):
        cursor = db.stories.find().sort([('rowid', -1)]).limit(1)
        try:
            rid = cursor[0]['rowid']
        except IndexError:
            rid = 0
        return rid


    def add_user(self, username, password):
        password = generate_password_hash(password)
        self.c.execute("INSERT INTO users VALUES(?, ?);", (username, password))
        self.db.commit()

    def update_user_password(self, username, new_password):
        password = generate_password_hash(new_password)
        self.c.execute("UPDATE users SET password=(?) WHERE username=(?);", (password, username))
        self.db.commit()

    #~get_ titles,content,authors were never used so I deleted them
    
    #~combined get_top_posts and get_top_posts_for_user
    #~userid = -1, all top posts otherwise for_user
    def get_top_posts(self, userid):
        if userid == -1:
            cursor = db.stories.find({'istop': '1'})
        else:
            cursor = db.stories.find({'istop':'1'},{'author':userid})
        l = []
        for document in cursor:
            l.append([document['rowid'], document['title']])
        return l

    #~returns list of lines linked to eachother by rowids
    def get_story_content(self, storyid):
        cursor = db.stories.find({'rowid':storyid})
        out = [cursor[0]['contents'],cursor[0]['link'],cursor[0]['author']]
        try:
            if out[1] != -1:
                insert = get_story_content(out[1])
                out = [(out[0],out[2])]
                out.extend(insert)
                return out
        except IndexError:
            return out
        return [(out[0], out[2])]

    #~returns the rowid of the line before storyid
    def get_lowest_child(self, storyid):
        cursor = db.stories.find({'rowid':storyid})
        out =[cursor[0]['rowid'],cursor[0]['link']]
        try:
            if out[1] != -1:
                return get_lowest_child(out[1])
        except IndexError:
            return out
        return out[0]

    def get_users(self):
        return parse_simple_selection(self.c.execute("SELECT username FROM users;").fetchall())

    def check_user_password(self, username, password):
        dat = self.c.execute("SELECT rowid, password FROM users WHERE username=(?);", (username,)).fetchone()
        if dat and check_password_hash(dat[1], password):
            return dat[0]
        return 0;

    def get_user_by_id(self, userid):
        return self.c.execute("SELECT username FROM users WHERE rowid=(?);", (str(userid),)).fetchone()[0]

    def remove_post(self, rowid):
        link = self.c.execute("SELECT link FROM stories WHERE rowid=(?);", (str(rowid),)).fetchone()
        print "ROWID", rowid
        self.c.execute("DELETE FROM stories WHERE rowid=(?);", (str(rowid),))
        self.db.commit()
        return link

    def remove_story(self, storyid):
        link = self.remove_post(storyid)
        if link > 0:
            self.remove_story(link)

def parse_simple_selection(output):
    members = []
    for member in output:
        members.append(member[0])
    return members

def format_schema(schema):
    output_match = []
    for table in schema:
        statement = u'CREATE TABLE ' + table[0] + ' ('
        for col in table[1]:
            statement += col[0] + ' ' + col[1] + ', '
        statement = statement[:-2] + ')'
        output_match.append((statement,))
    return output_match
