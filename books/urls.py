from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:user_id>/profile/', views.profile, name='profile'),
    path('<int:user_id>/favorites/', views.favorites, name='favorites'),
    path('user_requests/', views.user_requests, name='user_requests'),
    path('incoming_requests/', views.incoming_requests, name='incoming_requests'),
    path('new_book/', views.new_book, name='new_book'),
    path('book/<int:book_id>/', views.book_view, name='book_view'),
    path('edit_book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('author/<int:author_id>/', views.author, name='author'),
    path('category/<str:category>/<str:category_name>/', views.category, name='category'),
    path('book_request/', views.book_request, name='book_request'),
    path('fetch_book/', views.fetch_book, name='fetch_book'),
    path('cancel_request/', views.cancel_request, name='cancel_request'),
    path('accept_request/', views.accept_request, name='accept_request'),
    path('return_book/', views.return_book, name='return_book'),
]
