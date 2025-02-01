from django.urls import path
from . import views

#defining the urls for the catai app
urlpatterns = [
    #the home page of the catai app
    #'' means the root path
    path('', views.home, name='home'), 
    #the about page of the catai app
    path('about/', views.about, name='about'),
    
]