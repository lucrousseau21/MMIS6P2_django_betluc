from django.urls import path
from . import views

urlpatterns =[
    path('home',views.home , name='home'),
    path('',views.home , name='home2'),
    path('home/<str:film>',views.home , name='home3'),
    # path('liste',views.listeMovies , name='listeMovies'),
    # path('liste',views.listeMoviesTemplate , name='listeMovies'),
    path('liste',views.listeMoviesTemplate2 , name='listeMovies'),
    path('formulaire',views.formu , name='formulaire'),
]
