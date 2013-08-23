from dokku_controller.models import App, Deployment, Host, EnvironmentVariable, Domain, Revision
from django.contrib import admin


def delete_app(modeladmin, request, queryset):
    for app in queryset:
        app.delete()


def restart_app(modeladmin, request, queryset):
    for app in queryset:
        app.restart()


def deploy_app(modeladmin, request, queryset):
    for app in queryset:
        app.deploy()


class AppAdmin(admin.ModelAdmin):
    actions = [delete_app, restart_app, deploy_app]

admin.site.register(App, AppAdmin)
admin.site.register(Deployment)
admin.site.register(Host)
admin.site.register(Domain)
admin.site.register(EnvironmentVariable)
admin.site.register(Revision)