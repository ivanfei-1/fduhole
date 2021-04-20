from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        depth = 1

class DiscussionSerializer(serializers.ModelSerializer):
    first_post = PostSerializer()
    tag = TagSerializer(many=True)
    class Meta:
        model = Discussion
        exclude = ('mapping')
        depth = 1

    