#coding=utf8


import redis
import json
import random
from uuid import uuid1
from datetime import datetime, timedelta

from django.contrib.auth.models import User



article_24 = "article_24"
article_48 = "article_48"

R = redis.Redis()


def add_article(user, content):

    user_id = user.id
    article = {
            "id" : str(uuid1()),
            "content" : content,
            "user_id" : user_id,
            "create_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_liked_time" : None,
            }
    R.set("article_%s" % article["id"], json.dumps(article))
    R.sadd("article_24", article["id"])
    R.sadd("user_article_%s" % user_id, article["id"]) 
    R.set("article_score_%s" % article["id"], 0, ex = 24*60*60)

    return article["id"]

def user_like_article(user, article_id):

    user_id = user.id
    like_article_id = "like_article_%s" % article_id
    if not R.sismember(like_article_id, user_id):
        R.sadd(like_article_id, user_id)
        if R.sismember("article_24", article_id) and R.strlen("like_article_id") == 1:
            R.incr("article_score_%s" % article_id)
        article = json.loads(R.get("article_%s" % article_id))
        article["last_liked_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        R.set("article_%s" % article["id"], json.dumps(article))
    return True

def user_message_article(user, article_id, message):

    message = {
            "id" : str(uuid1()),
            "user_id" : user.id,
            "content" : message,
            "article_id" : article_id,
            "create_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
    R.set("message_%s" % message["id"], json.dumps(message))

    if not R.sismember("article_message_%s" % article_id, user.id):
        R.sadd("article_message_%s" % article_id, user.id)
        R.incr("article_score_%s" % article_id)
        if R.get("article_message_pets_%s" % article_id) is None:
            R.incrbyfloat("article_score_%s" % article_id, 1.5)
            R.set("article_message_pets_%s" % article_id, 1)


    return True

def Calculate_A():

    list_a = []
    standard_time = datetime.now() - timedelta(hours = 24)
    for article_id in R.smembers("article_24"):
        article = json.loads(R.get("article_%s" % article_id))
        
        if datetime.strptime(article["create_time"], "%Y-%m-%d %H:%M:%S") < standard_time:
            R.srem("article_24", article_id)
        else:
            list_a.append({
                            "id" : article_id,
                            "score": R.get("article_score_%s" % article_id)})
        

    return [json.loads(R.get("article_%s" % x["id"])) for x in sorted(list_a, key = lambda x : x["score"], reverse = True)[:100]]

def is_messaged_in_24hour(article_id): 

    standard_time = datetime.now() - timedelta(hours = 24)
    count = 0
    for message_id in R.smembers("article_message_%s" % article_id):
        message = json.loads(R.get("message_%s" % message_id))
        if message["create_time"] > standard_time:
            count = count + 1
    return count
    

def get_user_article_before_24hour(user_id):

    article_list = []
    standard_time = datetime.now() - timedelta(hours = 24)
    last_liked_time = datetime.now() - timedelta(hours = 24)

    for article_id in R.smembers("user_article_%s" % user_id):
        article = json.loads(R.get("article_%s" % article_id))
        if article["create_time"] < standard_time and \
            (article["last_liked_time"] > last_liked_time or \
            is_messaged_in_24hour(article["id"]) > 1):
            article_list.append(article)
    return article_list

def Calculate_B():

    list_b = []
    standard_time = datetime.now() - timedelta(hours = 48)
    users = User.objects.filter(last_login__gte =  standard_time)
    for user_id in users:
       list_b = list_b + get_user_article_before_24hour(user_id) 

    choiced_set = set()
    for x in xrange(len(list_b)):
        choiced_set.add(list_b[random.randint(0, len(list_b))])
        if len(choiced_set) == min(15, len(list_b)):
            break

    return choiced_set

def Calculate_hotpage():
    
    return sorted(Calculate_A() + Calculate_B(), key = lambda x: x["last_modified_time"], reverse = True)



