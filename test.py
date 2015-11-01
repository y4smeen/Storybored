import random
from pymongo import MongoClient


connection = MongoClient()

db = connection['test']

names = db.collection_names()
print names;

#--------------Methods for Editing-------------

#deletes all collections
def dropCollections(names):
    for i in range(len(names)):
        if i != 0:
            db.command("drop",names[i])

#prints collections
def printC(collect):
    for r in collect:
        print r

#-----------------Their Methods Redone--------------------

def add_story(title, author, contents, istop):
    rid = get_next_rowid() + 1
    db.stories.insert({'title':title,
                       'author': author,
                       'contents':contents,
                       'link':-1,
                       'rowid': rid,
                       'istop': istop})
    return rid
        
def update_story_link(story, link):
    db.stories.update({ 'rowid' : story },
                      { '$set' : { 'link' : link } })

#gets highest rowid in stories
def get_next_rowid():
    cursor = db.stories.find().sort([('rowid', -1)]).limit(1)
    try:
        rid = cursor[0]['rowid']
    except IndexError:
        rid = 0
    return rid

#gets all titles
#returns as list of lists containing
#rowid(same as storyid) and title 
def get_top_posts(userid):
    if userid == -1:
        cursor = db.stories.find({'istop': '1'})
    else:
        cursor = db.stories.find({'istop':'1'},{'author':userid})
    l = []
    for document in cursor:
        l.append([document['rowid'], document['title']])
    return l


#-------------testing------------------------------- 
dropCollections(names)

add_story("title",1,"this is a story.",'1')
add_story("t2",1,"another story",'1')
add_story("t3",4,"Once upon a time.",'1')

printC(db.stories.find())
printC(get_top_posts(-1))
