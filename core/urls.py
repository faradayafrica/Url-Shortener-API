#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.urls import path

from core.views import home, Redirect, Shorten, AjaxRedirect

app_name = 'core'

urlpatterns = [
    path('', home),
    path('api/shorten/', Shorten, name='shorten'),
    path('redirect/pause/', AjaxRedirect, name='pause-redirect'),
    path('<str:url>', Redirect, name='redirect')
]
