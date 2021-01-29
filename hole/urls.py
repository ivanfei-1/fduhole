from django.urls import path
from . import views

app_name = 'hole'
urlpatterns = [
    path('', views.index, name='index'),
    path('discussion/<int:discussion_id>/', views.discussion, name='discussion'),
    path('create_post/<int:discussion_id>/', views.create_post, name='create_post'),
    path('create_post/<int:discussion_id>/<int:post_id>/', views.create_post, name='reply_post'),
    path('create_discussion/', views.create_discussion, name='create_discussion'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('verify/<str:code>/', views.verify, name='verify'),
]
