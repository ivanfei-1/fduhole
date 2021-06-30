from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'is_active', 'is_staff', 'is_superuser')


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ('disabled', 'delete_reason')

    def to_representation(self, post):
        data = super().to_representation(post)
        if post.disabled:
            data['content'] = post.delete_reason
        if not self.context.get('user'):
            return data
        if post.discussion.name_mapping.filter(
            username__exact=self.context['user'].id,
            anonyname__exact=post.username
        ):
            data['is_me'] = True
        else:
            data['is_me'] = False
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        depth = 1


class DiscussionSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)

    class Meta:
        model = Discussion
        exclude = ('disabled',)
        depth = 1

    def to_representation(self, d):
        if d.disabled:
            return None
        data = super().to_representation(d)
        data['posts'] = PostSerializer(d.post_set.order_by('date_created').filter(
            disabled__exact=False)[:settings.INTERVAL], many=True).data
        data['first_post'] = PostSerializer(
            d.post_set.order_by('id')[0]).data
        data['last_post'] = PostSerializer(
            d.post_set.order_by('-id')[0]).data
        return data


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
