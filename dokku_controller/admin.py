from dokku_controller.models import App, Deployment, Host, EnvironmentVariable, Domain, Revision
from django.contrib import admin
from dokku_controller.tasks import scan_host_key


def delete_app(modeladmin, request, queryset):
    for app in queryset:
        app.delete()


def restart_app(modeladmin, request, queryset):
    for app in queryset:
        app.restart()


def start_app(modeladmin, request, queryset):
    for app in queryset:
        app.start()


def stop_app(modeladmin, request, queryset):
    for app in queryset:
        app.stop()


def pause_app(modeladmin, request, queryset):
    for app in queryset:
        app.pause()


def deploy_app(modeladmin, request, queryset):
    for app in queryset:
        app.deploy()


class AppAdmin(admin.ModelAdmin):
    actions = [delete_app, restart_app, deploy_app, pause_app, start_app, stop_app]

admin.site.register(App, AppAdmin)


class DeploymentAdmin(admin.ModelAdmin):
    list_display = ('app', 'host', 'status', 'revision')

admin.site.register(Deployment, DeploymentAdmin)


def scan_host(modeladmin, request, queryset):
    for host in queryset:
        scan_host_key(host.hostname)


class HostAdmin(admin.ModelAdmin):
    actions = [scan_host]

admin.site.register(Host, HostAdmin)
admin.site.register(Domain)
admin.site.register(EnvironmentVariable)


class RevisionAdmin(admin.ModelAdmin):
    search_fields = ('app__name', )
    list_display = ('revision_number', 'app')

admin.site.register(Revision, RevisionAdmin)