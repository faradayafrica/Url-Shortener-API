#   Copyright (c) Code Written and Tested by Ahmed Emad in 28/02/2020, 16:53

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls'), name='core')
]
