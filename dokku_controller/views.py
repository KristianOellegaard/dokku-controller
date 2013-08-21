import json
from django.http import Http404
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from dokku_controller.models import App, Domain, EnvironmentVariable


class ApplicationView(APIView):
    """
    Applications expose the following functions:

    GET
    ---

    Returns the app's name

    PUT
    ---

    Restarts the app

    DELETE
    ------

    Deletes the app completely, including any stored files
    """

    def get_app(self, args, kwargs):
        app_name = kwargs.get('app_name')
        try:
            app = App.objects.get(name=app_name)
        except App.DoesNotExist:
            raise Http404("App does not exist")
        return app

    def delete(self, request, *args, **kwargs):
        app = self.get_app(args, kwargs)
        app.delete()
        response = {}
        return Response(response)

    def put(self, request, *args, **kwargs):
        app = self.get_app(args, kwargs)
        app.update_environment_variables()
        response = {}
        return Response(response)

    def get(self, request, *args, **kwargs):
        app = self.get_app(args, kwargs)
        response = {
            'app_name': app.name,
        }
        return Response(response)


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('app', 'domain_name')


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class EnvironmentVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentVariable
        fields = ('app', 'key', 'value')


class EnvironmentVariableViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentVariable.objects.all()
    serializer_class = EnvironmentVariableSerializer