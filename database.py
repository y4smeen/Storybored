

from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

connection = MongoClient()
db = connection["storybored"]


def add_story(title, author, contents, istop):
    rid = get_next_rowid("stories") + 1
    db.stories.insert({'title':title,
                       'author':str(author),
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

#~gets highest rowid in collection
def get_next_rowid(collection):
    cursor = db[collection].find().sort([('rowid', -1)]).limit(1)
    try:
        rid = cursor[0]['rowid']
    except (IndexError, KeyError):
        rid = 0
    return rid


def add_user(username, password):
    password = generate_password_hash(password)
    db.users.insert({'username' : username,
                     'password' : password,
                     'rowid' : get_next_rowid('users')+1})

def update_user_password(username, new_password):
    password = generate_password_hash(new_password)
    db.users.update({'username' : username},
                    {'password': new_password})

#~get_ titles,content,authors were never used so I deleted them

#~combined get_top_posts and get_top_posts_for_user
#~userid = -1, all top posts otherwise for_user
def get_top_posts(userid):
    if userid == -1:
        cursor = db.stories.find({ 'rowid' : { '$exists': True}, 'istop': 1})
    else:
        cursor = db.stories.find({ 'rowid' : { '$exists': True}, 'istop':1,'author':str(userid)})
    l = []
    for doc in cursor:
        l.append([doc['rowid'],doc['title'],doc['author']])
    return l

#~returns list of lines linked to eachother by rowids
def get_story_content(storyid):
    cursor = db.stories.find({'rowid':int(storyid)})[0]
    out = [cursor['contents'],cursor['link'],cursor['author']]
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
    cursor = db.stories.find({'rowid' : int(storyid)})[0]
    out =[cursor['rowid'],cursor['link']]
    try:
        if out[1] != -1:
            return get_lowest_child(out[1])
    except IndexError:
        return out
    return out[0]



def remove_post(rowid):
    db.stories.remove({'rowid': rowid}, 1)

def remove_story(storyid):
    link = remove_post(storyid)
    if link > 0:
        remove_story(link)


def check_user_password(username, password):
	result = db.users.find_one({'username':username})
        if result != None and check_password_hash(result['password'],password):
            return result['rowid']
	return 0

def get_user_by_id(userid):
    document = db.users.find({'rowid' : int(userid)})[0]
    return document['username']

