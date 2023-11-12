from rest_framework import serializers
from tweets.models import Tweet
# from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework.exceptions import ValidationError

# 显示某个model对应的具体的object的
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'updated_at',
        )

# User is name of Model
# user is  instance of User
# user_id is primary key of User
# users is a list of users or quaryset of User

class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id = tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist'})
    # 必须return validated data, 即验证过后，进行过处理的输入数据
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id = validated_data['user_id'],
            tweet_id = validated_data['tweet_id'],
            content = validated_data['content'],
        )

class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content')

def update(self, instance, validated_data):
    instance.content = validated_data['content']
    instance.save()
    return instance


