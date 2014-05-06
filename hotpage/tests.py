# -*- coding: utf-8 -*-


import redis

from django.test import TestCase
from django.contrib.auth.models import User

from .views import add_article, user_like_article, user_message_article 
from .views import Calculate_A, Calculate_B
from .models import UserProfile


class HotpageTest(TestCase):
    
    def setUp(self):
        self.R = redis.Redis()
        self.user = User(username = "test")
        self.user.save()
        self.UserProfile = UserProfile(user = self.user, pets = True)
        self.UserProfile.save()
    

    def test_add_article(self):
        article_id = add_article(self.user, "test")
        self.article_id = article_id
        self.assertEqual(self.R.get("article_score_%s" % article_id), '0')
        self.assertTrue(self.R.sismember("article_24", article_id))
        self.assertTrue(self.R.sismember("user_article_%s" % self.user.id, article_id))
        self.assertIsNotNone(self.R.get("article_%s" % article_id))

    def test_user_like_article(self):
        article_id = add_article(self.user, "test")
        self.article_id = article_id
        score  = float(self.R.get("article_score_%s" % self.article_id))
        user_like_article(self.user, self.article_id)
        self.assertTrue(self.R.sismember("like_article_%s" % self.article_id, self.user.id))
        self.assertEqual(float(self.R.get("article_score_%s" % self.article_id)), score + 1)

    
    def test_user_message_article(self):
        article_id = add_article(self.user, "test")
        self.article_id = article_id
        score  = float(self.R.get("article_score_%s" % self.article_id))
        for x in xrange(2):
            user_message_article(self.user, article_id, "test")
            self.assertTrue(self.R.sismember("article_message_%s" % article_id, self.user.id))
            self.assertEqual(float(self.R.get("article_score_%s" % article_id)), score + 2.5)
        
    def test_Calculate_A(self):
        list_a = Calculate_A()
        self.assertTrue(len(list_a) <= 100)
        
    def test_Calculate_B(self):
        self.assertTrue(len(Calculate_B()) == 0)
