from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet


# 并非所有人都是admin可以增删查改，所以用ModelViewSet不合适
class TweetViewSet(viewsets.GenericViewSet):
    # queryset = Tweet.objects.all() 可不需要
    # serializer_class = TweetCreateSerializer
    serializer_class = TweetSerializerForCreate


    def get_permissions(self):
        if self.action =='list':
            return [AllowAny()]
        return [IsAuthenticated()]
    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        user_id = request.query_params['user_id']

        # select * from twitter_tweets
        # where user_id = xxx
        # order_by created_at desc
        # 这句SQL查询会用到user和created_at联合索引，单用user不够
        tweets = Tweet.objects.filter(user_id = user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # 一般来说json格式的response默认hash格式，而不能用List格式，所以需要套一个key: 'tweets'
        return Response({'tweets':serializer.data})


    def create(self, request):
        serializer = TweetSerializerForCreate(
            data = request.data,
            context = {'request':request},
        )
        if not serializer.is_valid():
            return Response({
                "success":False,
                "message":"Please check input",
                "errors":serializer.errors,
            }, status = 400)
        # tweet will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        return Response(TweetSerializer(tweet).data, status=201)