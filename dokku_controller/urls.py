from django.conf.urls import patterns, url, include
from dokku_controller.views import DomainViewSet, EnvironmentVariableViewSet, AppViewSet
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'domains', DomainViewSet)
router.register(r'environment_variables', EnvironmentVariableViewSet)
router.register(r'applications', AppViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
