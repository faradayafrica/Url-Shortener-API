#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.urls import path

from core.views import RedirectView, ShortenView, home

app_name = 'core'

urlpatterns = [
    path('', home),
    path('shorten', ShortenView.as_view(), name='shorten'),
    path('<str:url>', RedirectView.as_view(), name='redirect')
]
