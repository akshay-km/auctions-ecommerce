from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("createlisting",views.create_listing, name="createlisting"),
    path("categories", views.categories, name="categories"),
    path("category/<str:item>", views.category, name="category"),
    path("listing/<str:key>",views.listing, name="listing"),
    path("bid/<str:key>", views.bid, name="bid"),
    path("add/<str:key>",views.add_to_watchlist, name="add"),
    path("delete/<str:key>",views.delete_from_watchlist, name="delete"),
    path("close/<str:key>",views.close_bid, name="close"),
    path("addcomment/<str:key>",views.add_comment, name="addcomment"),
]
