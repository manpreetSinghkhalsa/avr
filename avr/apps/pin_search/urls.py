from django.conf.urls import url
from apps.pin_search import views as pin_search_views

# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = [
    url(r'^search/$', pin_search_views.SearchAPI.as_view(), name='search_api'),
]
