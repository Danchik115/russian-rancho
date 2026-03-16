from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/telegram', views.telegram_api, name='telegram_api'),
    path('about/', views.about_page, name='about'),
    path('families/', views.families_page, name='families'),
    path('kids/', views.kids_page, name='kids'),
    path('couples/', views.couples_page, name='couples'),
    path('groups/', views.groups_page, name='groups'),
    path('events/', views.events_page, name='events'),
    path('prices/', views.prices_page, name='prices'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('nedvizhimost/', views.nedvizhimost_page, name='nedvizhimost'),
]
