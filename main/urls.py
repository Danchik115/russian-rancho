from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/telegram', views.telegram_api, name='telegram_api'),
    path('api/birthday-subscribe', views.birthday_subscribe_api, name='birthday_subscribe_api'),
    path('cabinet/register/', views.cabinet_register_page, name='cabinet_register'),
    path('cabinet/login/', views.cabinet_login_page, name='cabinet_login'),
    path('cabinet/logout/', views.cabinet_logout, name='cabinet_logout'),
    path('cabinet/', views.cabinet_page, name='cabinet'),
    path('about/', views.about_page, name='about'),
    path('families/', views.families_page, name='families'),
    path('kids/', views.kids_page, name='kids'),
    path('couples/', views.couples_page, name='couples'),
    path('groups/', views.groups_page, name='groups'),
    path('events/', views.events_page, name='events'),
    path('prices/', views.prices_page, name='prices'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('nedvizhimost/', views.nedvizhimost_page, name='nedvizhimost'),
    path('nedvizhimost/domik-u-lesa/', views.domik_u_lesa_page, name='domik_u_lesa'),
    path('nedvizhimost/domik-u-pruda/', views.domik_u_pruda_page, name='domik_u_pruda'),
    path('nedvizhimost/teplaya-besedka-1/', views.teplaya_besedka_1_page, name='teplaya_besedka_1'),
    path('nedvizhimost/teplaya-besedka-2/', views.teplaya_besedka_2_page, name='teplaya_besedka_2'),
    path('nedvizhimost/letnyaya-besedka/', views.letnyaya_besedka_page, name='letnyaya_besedka'),
]
