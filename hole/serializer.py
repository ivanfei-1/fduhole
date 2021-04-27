from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'is_active', 'is_staff', 'is_superuser')

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
        exclude = ('mapping',)
        depth = 1

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    favored_discussion = DiscussionSerializer(many=True)
    class Meta:
        model = UserProfile
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('username',)
    from_user = UserSerializer()
    to_user = UserSerializer()
    class Meta:
        model = Message
        fields = '__all__'
    