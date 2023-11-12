from comments.models import Comment
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient
from tweets.models import Tweet

# Create your tests here.
class TestCase(DjangoTestCase):

    def create_user(self, username, email = None, password = None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # 不能写成User.objects.create()
        # 因为password需要加密，username和email需要进行一些normalize处理
        return User.objects.create_user(username,email,password)

    def create_tweet(self, user, content = None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user = user, content = content)

    def create_comment(self,user, tweet, content = None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)