from django.urls import path, include
from rest_framework.authtoken import views

from . import api
urlpatterns = [
    path('discussions/', api.DiscussionsView.as_view()),
    path('discussions/<int:pk>/', api.DiscussionsView.as_view()),
    path('posts/', api.PostsView.as_view()),
    path('tags/', api.TagsView.as_view()),
    path('login/', views.obtain_auth_token),
    path('register/', api.RegisterView.as_view()),
    path('verify/', api.VerifyView.as_view()),
    path('images/', api.ImagesView.as_view()),
]