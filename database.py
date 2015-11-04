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


connection = MongoClient()
db = connection["storybored"]


def add_story(title, author, contents, istop):
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
def update_story_link(story, link):
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


def add_user(username, password):
    password = generate_password_hash(password)
    db.users.insert({'username' : username, 
    				 'password' : password })

def update_user_password(username, new_password):
    password = generate_password_hash(new_password)
    c.execute("UPDATE users SET password=(?) WHERE username=(?);", (password, username))
    db.commit()

#~get_ titles,content,authors were never used so I deleted them

#~combined get_top_posts and get_top_posts_for_user
#~userid = -1, all top posts otherwise for_user
def get_top_posts(userid):
    if userid == -1:
        cursor = db.stories.find({'istop': '1'})
    else:
        cursor = db.stories.find({'istop':'1'},{'author':userid})
    l = []
    for document in cursor:
        l.append([document['rowid'], document['title']])
    return l

#~returns list of lines linked to eachother by rowids
def get_story_content(storyid):
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
def get_lowest_child(storyid):
    cursor = db.stories.find({'rowid':storyid})
    out =[cursor[0]['rowid'],cursor[0]['link']]
    try:
        if out[1] != -1:
            return get_lowest_child(out[1])
    except IndexError:
        return out
    return out[0]

def get_users(self):
    return parse_simple_selection(c.execute("SELECT username FROM users;").fetchall())

def check_user_password(username, password):
    dat = db.users.findOne({'username':username}, {'password': 1} )
    if check_password_hash(dat['password'], password):
        return dat[0]
    return 0

def get_user_by_id(userid):
    return c.execute("SELECT username FROM users WHERE rowid=(?);", (str(userid),)).fetchone()[0]

def remove_post(rowid):
    link = c.execute("SELECT link FROM stories WHERE rowid=(?);", (str(rowid),)).fetchone()
    print "ROWID", rowid
    c.execute("DELETE FROM stories WHERE rowid=(?);", (str(rowid),))
    db.commit()
    return link

def remove_story(storyid):
    link = remove_post(storyid)
    if link > 0:
        remove_story(link)


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
