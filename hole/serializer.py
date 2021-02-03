from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ReplyToSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__' 

class PostSerializer(serializers.ModelSerializer):
    reply_to = ReplyToSerializer()
    class Meta:
        model = Post
        fields = '__all__'
    # content = serializers.CharField()
    # username = serializers.CharField(max_length=191)
    # # reply_to = serializers.OneToOneField('Post', related_name='+', blank=True, null=True, on_delete=serializers.SET_NULL)
    # # discussion = serializers.ForeignKey(Discussion, on_delete=serializers.CASCADE)
    # date_created = serializers.DateTimeField(required=False)

class DiscussionSerializer(serializers.ModelSerializer):
    first_post = PostSerializer()
    class Meta:
        model = Discussion
        fields = '__all__'
    # count = serializers.IntegerField()
    # # tag = serializers.ManyToManyField(Tag, blank=True)
    # mapping = serializers.JSONField(required=False)
    # # first_post = serializers.OneToOneField('Post', related_name='+', null=True, on_delete=serializers.SET_NULL) 
    # date_created = serializers.DateTimeField(required=False)
    # date_updated = serializers.DateTimeField(required=False)
    