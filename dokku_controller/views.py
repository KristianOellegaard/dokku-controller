import json
from django.http import Http404
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from dokku_controller.models import App, Domain, EnvironmentVariable, Deployment, Revision


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('name',)


class AppViewSet(viewsets.ModelViewSet):
    """
    Apps exposes the following urls:

    /v1/applications/<appname\>/ **GET, POST, PUT, DELETE**
    -----------------------------------------------

    Get, create, update or delete an app.

    /v1/applications/<appname\>/start/ **POST**
    -------------------------------------

    Start an app

    /v1/applications/<appname\>/stop/ **POST**
    -------------------------------------

    Stop an app

    /v1/applications/<appname\>/restart/ **POST**
    -------------------------------------

    Restart an app

    /v1/applications/<appname\>/update_env_vars/ **POST**
    ---------------------------------------------

    Update the environment variables and restart the app

    /v1/applications/<appname\>/upload/ **POST**
    ------------------------------------

    Upload a new release of an app. Should only contain the file, such as:

    curl -i -F file=@upload.tar.gz https://<server\>/v1/applications/<app\>/upload/ -H 'Authorization: Token <token\>

    Must be a .tar.gz

    """
    queryset = App.objects.all()
    serializer_class = AppSerializer

    @action()
    def update_env_vars(self, request, pk=None):
        """
        Updates the environment variables and restarts the app
        """
        app = self.get_object()
        app.update_environment_variables()
        response = {}
        return Response(response)

    @action()
    def restart(self, request, pk=None):
        """
        Restarts the app
        """
        app = self.get_object()
        app.restart()
        response = {}
        return Response(response)

    @action()
    def start(self, request, pk=None):
        """
        Starts the app
        """
        app = self.get_object()
        app.restart()
        response = {}
        return Response(response)

    @action()
    def stop(self, request, pk=None):
        """
        Stops the app
        """
        app = self.get_object()
        app.restart()
        response = {}
        return Response(response)

    @action()
    def pause(self, request, pk=None):
        """
        Pause the app
        """
        app = self.get_object()
        app.pause()
        response = {}
        return Response(response)

    @action(parser_classes=(FileUploadParser, ))
    def upload(self, request, pk=None):
        """
        Upload a new release of an app. Should only contain the file in as in the file key.
        """
        app = self.get_object()
        deployment = Revision()
        deployment.compressed_archive = request.FILES['file']
        deployment.app = app
        deployment.save()
        app.deploy()
        response = {}
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
        fields = ('id', 'app', 'key', 'value')


class EnvironmentVariableViewSet(viewsets.ModelViewSet):
    """
    Apps exposes the following urls:

    /v1/environment_variables/<id\>/ **GET, POST, PUT, DELETE**
    -----------------------------------------------

    Get, create, update or delete an environment variable.

    """
    queryset = EnvironmentVariable.objects.all()
    serializer_class = EnvironmentVariableSerializer