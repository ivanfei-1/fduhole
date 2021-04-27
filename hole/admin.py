from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(Discussion)
admin.site.register(Post)
admin.site.register(Mapping)
admin.site.register(Tag)
admin.site.register(Report)