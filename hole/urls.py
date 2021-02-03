from django.urls import path, include

from . import views

app_name = 'hole'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:page>/', views.index, name='index_page'),
    path('discussion/<int:discussion_id>/', views.discussion, name='discussion'),
    path('discussion/<int:discussion_id>/<int:page>/', views.discussion, name='discussion_page'),
    path('create_post/<int:discussion_id>/', views.create_post, name='create_post'),
    path('create_post/<int:discussion_id>/<int:post_id>/', views.create_post, name='reply_post'),
    path('create_discussion/', views.create_discussion, name='create_discussion'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('verify/<str:code>/', views.verify, name='verify'),
]

# router = DefaultRouter()
# router.register('discussions', views.DiscussionsViewSet)

# urlpatterns += [
#     path('', include(router.urls)),
# ]