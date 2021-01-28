from django.db import models

# Create your models here.
class TempUser(models.Model):
    username = models.CharField(max_length=191)
    password = models.CharField(max_length=191)
    email = models.EmailField(max_length=191, primary_key=True)
    code = models.CharField(max_length=191)
    def __str__(self):
        return self.email + ':' + self.username

class Tag(models.Model):
    name = models.CharField(max_length=191, primary_key=True)
    count = models.IntegerField(db_index=True)
    def __str__(self):
        return self.name


class Discussion(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True,db_index=True)
    count = models.IntegerField()
    tag = models.ManyToManyField(Tag, blank=True)
    mapping = models.JSONField(null=True, blank=True)
    first_post = models.IntegerField(null=True)
    def __str__(self):
        return str(self.pk)

class Post(models.Model):
    content = models.TextField()
    username = models.CharField(max_length=191)
    date_created = models.DateTimeField(auto_now_add=True,db_index=True)
    reply_to = models.IntegerField(null=True, blank=True)
    # number = models.IntegerField(db_index=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.pk)
