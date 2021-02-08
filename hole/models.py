from django.db import models

# Create your models here.
class TempUser(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    email = models.EmailField(max_length=32, primary_key=True)
    code = models.CharField(max_length=191)
    def __str__(self):
        return self.email + ':' + self.username

class Tag(models.Model):
    name = models.CharField(max_length=8, primary_key=True)
    count = models.IntegerField(db_index=True, default='0')
    color = models.CharField(max_length=32, default='blue')
    def __str__(self):
        return self.name


class Discussion(models.Model):
    count = models.IntegerField()
    tag = models.ManyToManyField(Tag, blank=True)
    mapping = models.JSONField(null=True, blank=True)
    first_post = models.OneToOneField('Post', related_name='+', null=True, on_delete=models.SET_NULL) # on_delete null 需要进一步设置
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True,db_index=True)
    def __str__(self):
        return '#' + str(self.pk) + ' ' + self.first_post.content[:100]

class Post(models.Model):
    content = models.TextField()
    username = models.CharField(max_length=191)
    reply_to = models.OneToOneField('Post', related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True,db_index=True)
    def __str__(self):
        return '#' + str(self.pk) + ' ' + self.content[:100]
