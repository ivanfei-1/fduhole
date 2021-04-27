from django.urls import path, include
from rest_framework.authtoken import views
# from rest_framework.documentation import include_docs_urls

from . import api
urlpatterns = [
    # path('docs/', include('rest_framework_docs.urls')),
    path('login/', views.obtain_auth_token),
    path('register/', api.RegisterView.as_view()),
    path('profile/', api.UserProfileView.as_view()),
    path('discussions/', api.DiscussionsView.as_view()),
    path('posts/', api.PostsView.as_view()),
    path('tags/', api.TagsView.as_view()),
    path('images/', api.ImagesView.as_view()),
    path('reports/', api.ReportView.as_view()),
    path('email/', api.EmailView.as_view()),
    path('message/', api.MessageView.as_view()),
]