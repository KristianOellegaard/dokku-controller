from dokku_controller.models import App, Deployment, Host, EnvironmentVariable, Domain
from django.contrib import admin


def delete_app(modeladmin, request, queryset):
    for app in queryset:
        app.delete()


def restart_app(modeladmin, request, queryset):
    for app in queryset:
        app.restart()


class AppAdmin(admin.ModelAdmin):
    actions = [delete_app, restart_app]

admin.site.register(App, AppAdmin)
admin.site.register(Deployment)
admin.site.register(Host)
admin.site.register(Domain)
admin.site.register(EnvironmentVariable)