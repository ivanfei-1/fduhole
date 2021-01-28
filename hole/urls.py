from django.urls import path
from . import views

app_name = 'hole'
urlpatterns = [
    path('', views.index, name='index'),
    path('discussion/<int:pk>/', views.discussion, name= 'discussion'),
    path('login/', views.login, name= 'login'),
    path('logout/', views.logout, name= 'logout'),
    path('register/', views.register, name= 'register'),
    path('verify/<str:code>/', views.verify, name= 'verify'),
]
