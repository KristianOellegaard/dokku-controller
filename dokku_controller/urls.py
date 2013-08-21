from django.conf.urls import patterns, url, include
from dokku_controller.views import ApplicationView, DomainViewSet, EnvironmentVariableViewSet
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'domains', DomainViewSet)
router.register(r'environment_variables', EnvironmentVariableViewSet)

urlpatterns = patterns('',
    url(r'^applications/(?P<app_name>\w+)/$', ApplicationView.as_view(), name='app_view'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
