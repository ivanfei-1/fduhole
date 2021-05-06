import django, os, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fduhole.settings")
django.setup()

from hole.models import *

for d in Discussion.objects.all():
    d.count = d.post_set.count()
    d.save()

for t in Tag.objects.all():
    t.count = t.discussion_set.count()
    t.save()

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '更新计数完成')