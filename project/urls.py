from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^v1/', include('dokku_controller.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
