from django.urls import path, include
from rest_framework.authtoken import views

from . import v1
urlpatterns = [
    path('login/', views.obtain_auth_token),
    path('register/', v1.RegisterView.as_view()),
    path('profile/', v1.UserProfileView.as_view()),
    path('discussions/', v1.DiscussionsView.as_view()),
    path('posts/', v1.PostsView.as_view()),
    path('tags/', v1.TagsView.as_view()),
    path('images/', v1.ImagesView.as_view()),
    path('reports/', v1.ReportView.as_view()),
    path('email/', v1.EmailView.as_view()),
    path('message/', v1.MessageView.as_view()),
    path('admin/', v1.PostsAdminView.as_view()),
]
