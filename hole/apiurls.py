from django.urls import path, include
from rest_framework.authtoken import views
# from rest_framework.documentation import include_docs_urls

from . import api
urlpatterns = [
    # path('docs/', include('rest_framework_docs.urls')),
    path('discussions/', api.DiscussionsView.as_view()),
    path('discussions/<int:pk>/', api.DiscussionsView.as_view()),
    path('posts/', api.PostsView.as_view()),
    path('tags/', api.TagsView.as_view()),
    path('login/', views.obtain_auth_token),
    path('register/', api.RegisterView.as_view()),
    path('images/', api.ImagesView.as_view()),
]