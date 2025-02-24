from django.contrib import admin
from django.urls import path
from game import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('game/', views.game_view, name='game'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('add-word/', views.add_word, name='add_word'),
]


