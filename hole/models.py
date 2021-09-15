from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=8, primary_key=True)
    count = models.IntegerField(db_index=True, default='0')
    color = models.CharField(max_length=32, default='blue')

    def __str__(self):
        return self.name


class Discussion(models.Model):
    count = models.IntegerField(db_index=True, default='0')
    tag = models.ManyToManyField(Tag, blank=True)
    # first_post = models.OneToOneField('Post', related_name='+', null=True, on_delete=models.SET_NULL) # on_delete null 需要进一步设置
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)
    is_folded = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return '#' + str(self.pk) + ' ' + self.post_set.order_by('id')[0].content[:100]


class Post(models.Model):
    content = models.TextField()
    delete_reason = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=16)
    reply_to = models.IntegerField(blank=True, null=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return '#' + str(self.pk) + ' ' + self.content[:100]


class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    dealed = models.BooleanField(default=False)

    def __str__(self):
        return '帖子#{}，{}'.format(self.post.pk, self.reason)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    favored_discussion = models.ManyToManyField(Discussion, blank=True)
    encrypted_email = models.CharField(max_length=200, blank=True)
    has_input_email = models.BooleanField(default=False)
    registered_from_app = models.BooleanField(default=False)
    ban_visit_permanent = models.BooleanField(default=False)
    ban_visit_until = models.BooleanField(null=True, blank=True)
    ban_post_permanent = models.BooleanField(default=False)
    ban_post_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}".format(self.user.__str__())


class Mapping(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    anonyname = models.CharField(max_length=16)
    discussion = models.ForeignKey(
        Discussion, related_name='name_mapping', on_delete=models.CASCADE)

    def __str__(self):
        return '#{}: {} -> {}'.format(self.discussion.pk, self.username.username, self.anonyname)


class Message(models.Model):
    from_user = models.ForeignKey(
        User, related_name='message_from', on_delete=models.CASCADE, db_index=True)
    to_user = models.ForeignKey(
        User, related_name='message_to', on_delete=models.CASCADE, db_index=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} -> {}: {}'.format(self.from_user.username, self.to_user.username, self.content)
