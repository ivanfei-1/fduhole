from django.contrib import admin
from .models import TempUser, Tag, Discussion, Post
# Register your models here.
admin.site.register(Post)
admin.site.register(Discussion)
admin.site.register(Tag)
admin.site.register(TempUser)