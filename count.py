import django, os, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fduhole.settings")
django.setup()

from hole.models import *

# for d in Discussion.objects.all():
#     d.count = d.post_set.filter(disabled__exact=False).count() - 1
#     d.save()

for t in Tag.objects.all():
    t.count = t.discussion_set.filter(disabled__exact=False).count()
    t.save()

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '更新计数完成')
