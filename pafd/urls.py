from django.urls import path
from . import views

app_name = 'pafd'
urlpatterns = [
    path('', views.index, name='index'),
    path('invalid/', views.invalid, name= 'invalid'),
    path('validated/',views.validated, name='validated'),
#    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
]
