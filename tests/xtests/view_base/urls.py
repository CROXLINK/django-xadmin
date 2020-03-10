from __future__ import absolute_import
from django.urls import re_path, include
from .adminx import site


urlpatterns = [
    re_path(r'', include(site.urls, namespace='xadmin')),
]
