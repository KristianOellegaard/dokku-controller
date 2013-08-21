from django.conf.urls import patterns, url, include

from dokku_controller.views import ApplicationView

urlpatterns = patterns('',
    url(r'^(?P<app_name>\w+)/$', ApplicationView.as_view(), name='app_view'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
