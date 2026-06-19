from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
	path('sectors/', views.sectors_list, name='sectors_list'),
	path('sectors/today/', views.sectors_today, name='sectors_today'),
	path('sectors/card/<int:card_id>/', views.card_news_detail, name='card_news_detail'),
	path('sectors/<int:sector_id>/stocks/', views.sector_stocks, name='sector_stocks'),
]
