from django.urls import path
from . import views

urlpatterns = [
    path("login/",    views.LoginView.as_view(),    name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/",  views.ProfileView.as_view(),  name="profile"),
    path("watchlists/",         views.WatchlistView.as_view(),       name="watchlist-list"),
    path("watchlists/<int:pk>/", views.WatchlistDetailView.as_view(), name="watchlist-detail"),
    path("watchlists/<int:pk>/add/",    views.AddToWatchlistView.as_view(),    name="add-to-watchlist"),
    path("watchlists/<int:pk>/remove/", views.RemoveFromWatchlistView.as_view(), name="remove-from-watchlist"),
]