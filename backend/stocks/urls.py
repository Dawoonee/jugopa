from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('save/', views.save_stocks, name='save_stocks'),
    path('', views.stock_list_create, name='stock_list_create'),
    path('top-performer/', views.top_performer, name='top_performer'),
    path('<str:stock_code>/', views.stock_detail, name='stock_detail'),
]
