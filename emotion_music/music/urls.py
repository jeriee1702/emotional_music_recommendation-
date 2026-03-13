from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('search/', views.search, name='search'),
    path('favorites/', views.favorites, name='favorites'),
    path('playlists/', views.playlists_view, name='playlists'),
    path('playlists/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('recent/', views.recently_played_view, name='recently_played'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # AJAX / action endpoints
    path('favorite/toggle/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('playlists/add/', views.add_to_playlist, name='add_to_playlist'),
    path('mark-played/<int:pk>/', views.mark_played, name='mark_played'),
    path('download/<int:pk>/', views.download_song, name='download_song'),
]