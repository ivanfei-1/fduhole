from django.contrib import admin
from .models import *

from django.utils.html import format_html
from django.urls import reverse


def linkify(field_name):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """
    def _linkify(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return '-'
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f'admin:{app_label}_{model_name}_change'
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify.short_description = field_name  # Sets column name
    return _linkify


class PostInline(admin.TabularInline):
    model = Post

# class UserProfileInline(admin.TabularInline):
#     model = UserProfile


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    inlines = [PostInline]
    fields = ('is_folded', 'disabled', 'tag', 'date_updated', 'date_created')
    readonly_fields = ('date_updated', 'date_created',)
    list_display = ('__str__', 'is_folded', 'disabled',
                    'date_updated', 'date_created')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['content']
    fields = ('content', 'discussion', 'username',
              'reply_to', 'disabled', 'delete_reason')
    readonly_fields = ('date_created',)
    list_display = ('__str__', linkify('discussion'), 'username',
                    'reply_to', 'date_created', 'disabled')

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):


admin.site.register(Mapping)
admin.site.register(Tag)
admin.site.register(Report)
# admin.site.register(UserProfile)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    fields = ('user', 'favored_discussion', 'encrypted_email', 'has_input_email', 'registered_from_app', 'ban_post_permanent', 'ban_post_until')
