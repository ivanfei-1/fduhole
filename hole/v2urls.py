from django.urls import path, include
from rest_framework.authtoken import views

from . import v2
urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('register/', v2.RegisterView.as_view()),
    path('profile/', v2.UserProfileView.as_view()),
    path('discussions/', v2.DiscussionsView.as_view()),
    path('posts/', v2.PostsView.as_view()),
    path('tags/', v2.TagsView.as_view()),
    path('images/', v2.ImagesView.as_view()),
    path('reports/', v2.ReportView.as_view()),
    path('email/', v2.EmailView.as_view()),
    path('message/', v2.MessageView.as_view()),
]