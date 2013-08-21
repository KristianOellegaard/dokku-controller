import json
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from dokku_controller.models import App


class ApplicationView(APIView):

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
        app.restart()
        response = {}
        return Response(response)