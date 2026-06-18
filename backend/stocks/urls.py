from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('save/', views.save_stocks, name='save_stocks'),
    path('', views.stock_list_create, name='stock_list_create'),
    path('search/', views.stock_search, name='stock_search'),
    path('indices/', views.market_indices, name='market_indices'),
    path('weather/today/', views.market_weather_today, name='market_weather_today'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmarks/<str:stock_code>/', views.bookmark_delete, name='bookmark_delete'),
    path('top-performer/', views.top_performer, name='top_performer'),
    path('<str:stock_code>/', views.stock_detail, name='stock_detail'),
]
