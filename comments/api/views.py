from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# from django_filters import rest_framework as filters


# 并非所有人都是admin可以增删查改，所以用ModelViewSet不合适
class CommentViewSet(viewsets.ModelViewSet):
    # 只实现List,create,update, destroy的方法
    # 不实现retrieve （查询单个需求），因为没这个需求

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # POST / api/comments/  -> create
    # GET    / api/comments/  -> list
    # GET / api/comments/1/  -> retrieve
    # DELETE / api/comments/1/  -> destroy
    # PATCH / api/comments/1/  -> partial_update
    # PUT / api/comments/1/  -> update



    def get_permissions(self):
        if self.action =='create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(),IsObjectOwner()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        if 'tweet_id' not in request.query_params:
            return Response({
                'message':'Please check input',
                'success': False,
            }, status = status.HTTP_400_BAD_REQUEST,
            )
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id = tweet_id)

        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'comments':serializer.data
        }, status = status.HTTP_200_OK)

    def create(self,request,*args,**kwargs):
        data = {
            'user_id':request.user_id,
            'tweet_id':request.data.get('tweet_id'),
            'content':request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data=data)

        if not serializer.is_valid():
            return Response({
                'message':'Please check input',
                'errors':serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save 方法会触发serializer 里的creaete方法，
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=201,
        )

    def update(self, request, *args, **kwargs):
        serializer = CommentSerializerForUpdate(
            # get_object 是DRF包装的一个函数，会在找不到的时候raise 404 Error，是两行的合并
            # comment = self.get_object()
            # instance = comment
            instance = self.get_object(),
            data = request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input'
            }, status = status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status = status.HTTP_200_OK,
        )

    def destroy(self,request, *args,**kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({
            'success': True
        }, status = status.HTTP_200_OK)