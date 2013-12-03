from models import *
from django.contrib import admin


class ServicePlanInline(admin.TabularInline):
    model = ServicePlan


class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServicePlanInline]
    readonly_fields = ('base_url','regions')

admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceAssociation)