from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL ='/api/comments/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # 必须登录
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 必须带content
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        # 只有tweet_id不行
        response = self.linghu_client.post(COMMENT_URL,{'tweet_id':self.tweet_id})
        self.assertEqual(response.status_code, 400)
        # 只有content也不行
        response = self.linghu_client.post(COMMENT_URL,{'content':'1'})
        self.assertEqual(response.status_code, 400)
        # content太长不行
        response = self.linghu_client.post(COMMENT_URL,{
            'tweet_id':self.tweet_id,
            'content':'1'*141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'],True)

        # 正常发帖
        tweets_count = Tweet.objects.count()
        response = self.linghu_client.post(COMMENT_URL, {
            'tweet_id': self.tweet_id,
            'content':'HELLO WORLD, this is my first tweet!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')


    def test_destroy(self):
        comment = self.create_comment(self.linghu,self.tweet)
        url = '{}{}/'.format((COMMENT_URL), comment.id)

        # 匿名不可删除
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code,403)

        # 非本人不可删除
        response = self.dongxie_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 本人可以删除
        count = Comment.objects.count()
        response = self.linghu_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count -1)

    def test_update(self):
        comment = self.create_comment(self.linghu,self.tweet, 'original')
        another_tweet = self.create_tweet(self.dongxie)
        url = '{}{}/'.format((COMMENT_URL), comment.id)

        # 匿名不可更新
        response = self.anonymous_client.put(url, {'content':'new'})
        self.assertEqual(response.status_code,403)

        # 非本人不可更新
        response = self.dongxie_client.put(url, {'content':'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')

        # 不能更新除content外的内容
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(url, {
            'content':'new',
            'user_id':self.dongxie.id,
            'tweet_id':another_tweet.id,
            'created_at':now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content,'new')
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at,now)
        self.assertNotEqual(comment.updated_at, before_updated_at)


